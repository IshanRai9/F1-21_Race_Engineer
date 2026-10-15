"""Validate datagrams and pair telemetry/lap readings from the same game frame."""

import math
import struct
import time

from packets import (PacketHeader, parse_session_data, parse_player_lap_data,
                     parse_player_telemetry)
from web_hud import update_web_state, TELEMETRY_TIMEOUT

PACKET_SIZES = {1: 625, 2: 970, 6: 1347}


def newer_frame(frame: int, previous: int) -> bool:
    return 0 < (frame - previous) % (2 ** 32) < 2 ** 31


class TelemetryStream:
    def __init__(self, analysis):
        self.analysis = analysis
        self.session_uid = None
        self.retired_sessions = set()
        self.latest_session = None
        self.latest_lap = None
        self.latest_telemetry = None
        self.last_frames = {}
        self.pending = {}
        self.last_processed_frame = None
        self.last_pair_time = None
        self.context_start_time = 0.0
        self.last_error = None

    def check_timeout(self, now=None):
        now = time.monotonic() if now is None else now
        if self.last_pair_time is not None and now - self.last_pair_time > TELEMETRY_TIMEOUT:
            update_web_state({'connected': False})
            self.analysis.delta.current_lap_invalid = True
            self.analysis.previous_corner_sample = None
            self.pending.clear()

    def handle(self, data: bytes, now=None) -> bool:
        now = time.monotonic() if now is None else now
        self.check_timeout(now)
        self.last_error = None
        try:
            header = PacketHeader.from_bytes(data)
            packet_id = header.packet_id
            if packet_id not in PACKET_SIZES:
                return False
            if (header.packet_format != 2021 or header.packet_version != 1
                    or len(data) != PACKET_SIZES[packet_id]
                    or not 0 <= header.player_car_index < 22
                    or not math.isfinite(header.session_time)):
                raise ValueError('Wrong packet format, version, length, timestamp, or player index')
            if packet_id == 1:
                payload = parse_session_data(data)
                if not (payload.track_id >= 0 and payload.track_length > 0):
                    return False
            elif packet_id == 2:
                payload = parse_player_lap_data(data, header.player_car_index)
                if not all(math.isfinite(value) for value in
                           (payload.lap_distance, payload.total_distance, payload.safety_car_delta)):
                    raise ValueError('Non-finite lap data')
                if payload.sector not in (0, 1, 2) or payload.pit_status not in (0, 1, 2):
                    raise ValueError('Invalid lap state')
            else:
                payload = parse_player_telemetry(data, header.player_car_index)
                controls = (payload.throttle, payload.brake)
                if (not all(math.isfinite(x) and 0 <= x <= 1 for x in controls)
                        or not math.isfinite(payload.steer) or not -1 <= payload.steer <= 1
                        or not all(math.isfinite(x) and x >= 0 for x in payload.tyres_pressure)
                        or not -1 <= payload.gear <= 8 or payload.speed > 600):
                    raise ValueError('Invalid car telemetry')
        except (ValueError, struct.error) as error:
            self.last_error = str(error)
            return False

        if header.session_uid != self.session_uid:
            # Only a session packet can establish which track incoming readings belong to.
            if packet_id != 1 or header.session_uid in self.retired_sessions:
                return False
            if self.session_uid is not None:
                self.retired_sessions.add(self.session_uid)
            self.session_uid = header.session_uid
            self.last_frames.clear()
            self.last_processed_frame = None

        previous = self.last_frames.get(packet_id)
        if previous is not None and not newer_frame(header.frame_identifier, previous):
            return False
        self.last_frames[packet_id] = header.frame_identifier

        if packet_id == 1:
            previous_context = self.analysis.session_context
            self.analysis.update_session(payload, header.session_uid)
            self.latest_session = payload
            if previous_context != self.analysis.session_context:
                self.pending.clear()
                self.latest_lap = self.latest_telemetry = None
                self.last_pair_time = None
                self.last_processed_frame = None
                self.context_start_time = header.session_time
            return False

        if header.session_time < self.context_start_time:
            return False
        frame = header.frame_identifier
        if self.last_processed_frame is not None and not newer_frame(frame, self.last_processed_frame):
            return False
        pair = self.pending.setdefault(frame, {})
        pair[packet_id] = (payload, now, header.session_time)
        while len(self.pending) > 8:
            self.pending.pop(next(iter(self.pending)))
        if 2 not in pair or 6 not in pair:
            return False
        self.pending.pop(frame, None)
        lap, lap_arrival, lap_time = pair[2]
        telemetry, telemetry_arrival, telemetry_time = pair[6]
        if abs(lap_arrival - telemetry_arrival) > 0.5 or abs(lap_time - telemetry_time) > 0.05:
            return False
        self.latest_lap, self.latest_telemetry = lap, telemetry
        self.last_processed_frame = frame
        self.last_pair_time = now
        self.analysis.update_telemetry(telemetry, lap)
        update_web_state({'last_update_monotonic': now})
        return True
