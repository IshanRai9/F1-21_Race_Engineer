"""
Analysis Engine — The Race Engineer's Brain
=============================================
Real-time telemetry analysis producing:
  1. Verbal callouts (Braking points, tyre temps, lap/sector deltas, setups)
  2. Live Web HUD telemetry streaming
  3. Corner-by-corner analysis of "Why You Are Slower"
  4. Real-time speed trace comparison vs session best
"""

import time
from dataclasses import dataclass, field
from typing import Optional

from packets import CarTelemetryData, LapData, SessionData, TRACK_NAMES, SESSION_TYPES
from track_data import get_braking_points, get_setup_advice
from voice_engine import VoiceEngine, Priority
from web_hud import update_web_state, add_voice_log


# ──────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────
TYRE_TEMP_HIGH = 104     # °C – surface temp above this = overheating
TYRE_TEMP_LOW = 80       # °C – surface temp below this = cold
TYRE_TEMP_CRITICAL = 112 # °C – critical degradation
TYRE_TEMP_SUSTAIN_SECS = 2.5

BRAKING_WARN_DISTANCE = 220  # Metres before braking zone to announce

DELTA_SAMPLE_INTERVAL = 10.0  # Metres between samples for trace
DELTA_REPORT_INTERVAL = 14.0  # Seconds between voice delta callouts

WHEEL_NAMES = ("Rear Left", "Rear Right", "Front Left", "Front Right")

# Corner definitions for Silverstone (Track ID 7)
SILVERSTONE_CORNERS = [
    {"name": "Turn 1 Abbey", "start": 180, "end": 450, "ref_apex": 275, "ref_brake": 290},
    {"name": "Turn 3 Village", "start": 700, "end": 1000, "ref_apex": 110, "ref_brake": 850},
    {"name": "Turn 4 The Loop", "start": 1000, "end": 1200, "ref_apex": 88, "ref_brake": 1050},
    {"name": "Turn 6 Brooklands", "start": 1600, "end": 1950, "ref_apex": 140, "ref_brake": 1750},
    {"name": "Turn 7 Luffield", "start": 1950, "end": 2250, "ref_apex": 115, "ref_brake": 2000},
    {"name": "Turn 9 Copse", "start": 2700, "end": 3050, "ref_apex": 255, "ref_brake": 2820},
    {"name": "Maggots-Becketts", "start": 3250, "end": 3850, "ref_apex": 220, "ref_brake": 3350},
    {"name": "Turn 15 Stowe", "start": 4800, "end": 5200, "ref_apex": 185, "ref_brake": 4950},
    {"name": "Turn 16 Vale Chicane", "start": 5300, "end": 5600, "ref_apex": 95, "ref_brake": 5420},
    {"name": "Turn 17-18 Club", "start": 5600, "end": 5850, "ref_apex": 150, "ref_brake": 5680},
]


@dataclass
class TyreState:
    hot_since: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0])
    cold_since: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0])
    last_alert_time: float = 0.0


@dataclass
class DeltaTracker:
    # Best lap: distance -> elapsed_time_ms
    best_lap_times: dict[float, int] = field(default_factory=dict)
    best_lap_speeds: list[list[float]] = field(default_factory=list)  # [[dist, speed], ...]
    best_lap_time_ms: int = 0
    best_lap_num: int = 0

    # Current lap
    current_lap_times: dict[float, int] = field(default_factory=dict)
    current_lap_speeds: list[list[float]] = field(default_factory=list)
    current_lap_num: int = 0
    current_lap_invalid: bool = False
    last_sample_distance: float = -999.0

    # Timing
    last_delta_report_time: float = 0.0
    last_reported_delta_ms: int = 0


class AnalysisEngine:
    """The brain of the AI Race Engineer."""

    def __init__(self, voice: VoiceEngine):
        self.voice = voice

        self.tyre_state = TyreState()
        self.delta = DeltaTracker()
        self.session: Optional[SessionData] = None
        self.track_id: int = 7  # Default to Silverstone
        self.track_name: str = "Silverstone"
        self.braking_points: list[tuple[float, str, str]] = []
        self.announced_braking: set[str] = set()
        self.last_lap_num: int = 0
        self.last_position: int = 0
        self.last_sector: int = 0
        self.session_started = False
        self.setup_advice_given = False

        # Corner tracking
        self.corners = SILVERSTONE_CORNERS
        self.current_corner_data: dict[str, dict] = {}
        self.best_corner_data: dict[str, dict] = {}
        self.corner_diagnostics: list[dict] = []

        # Load initial track data
        self.braking_points = get_braking_points(7)

    # ──────────────────────────────────────────
    # Session Handling
    # ──────────────────────────────────────────

    def update_session(self, session: SessionData):
        self.session = session
        self.track_id = session.track_id
        self.track_name = TRACK_NAMES.get(session.track_id, f"Track {session.track_id}")
        session_type = SESSION_TYPES.get(session.session_type, "Session")

        # Load braking points
        self.braking_points = get_braking_points(session.track_id)
        if session.track_id == 7:
            self.corners = SILVERSTONE_CORNERS
        else:
            self.corners = []

        if not self.session_started:
            self.session_started = True
            msg = (
                f"Engineer online. Welcome to {self.track_name}. {session_type}. "
                f"Track temperature {session.track_temperature} degrees. "
                f"Braking points and live delta tracker online. Let's go."
            )
            self.speak(msg, Priority.CRITICAL)

    def speak(self, message: str, priority: Priority = Priority.NORMAL):
        """Speak via TTS and record in web HUD radio log."""
        add_voice_log(message)
        self.voice.say(message, priority)

    # ──────────────────────────────────────────
    # Tyre Temperature Analysis
    # ──────────────────────────────────────────

    def analyze_tyres(self, telemetry: CarTelemetryData, lap: LapData):
        now = time.time()
        temps = telemetry.tyres_surface_temperature

        if telemetry.speed < 40:
            return

        hot_wheels = []
        cold_wheels = []
        critical_wheels = []

        for i in range(4):
            temp = temps[i]
            if temp >= TYRE_TEMP_CRITICAL:
                critical_wheels.append((WHEEL_NAMES[i], temp))
            elif temp > TYRE_TEMP_HIGH:
                if self.tyre_state.hot_since[i] == 0.0:
                    self.tyre_state.hot_since[i] = now
                elif now - self.tyre_state.hot_since[i] >= TYRE_TEMP_SUSTAIN_SECS:
                    hot_wheels.append((WHEEL_NAMES[i], temp))
            else:
                self.tyre_state.hot_since[i] = 0.0

            if temp < TYRE_TEMP_LOW:
                if self.tyre_state.cold_since[i] == 0.0:
                    self.tyre_state.cold_since[i] = now
                elif now - self.tyre_state.cold_since[i] >= TYRE_TEMP_SUSTAIN_SECS:
                    cold_wheels.append((WHEEL_NAMES[i], temp))
            else:
                self.tyre_state.cold_since[i] = 0.0

        if now - self.tyre_state.last_alert_time < 25.0:
            return

        if critical_wheels:
            names = " and ".join(w[0] for w in critical_wheels)
            self.speak(
                f"Critical! {names} overheating at {critical_wheels[0][1]} degrees! Manage your tyres!",
                Priority.HIGH
            )
            self.tyre_state.last_alert_time = now
        elif hot_wheels:
            fronts = [w for w in hot_wheels if "Front" in w[0]]
            rears = [w for w in hot_wheels if "Rear" in w[0]]
            if fronts and rears:
                self.speak(f"All tyres running hot above {TYRE_TEMP_HIGH} degrees. Manage entry speeds.", Priority.NORMAL)
            elif fronts:
                avg = sum(w[1] for w in fronts) // len(fronts)
                self.speak(f"Front tyres overheating at {avg} degrees. Ease off entry steering angle.", Priority.NORMAL)
            elif rears:
                avg = sum(w[1] for w in rears) // len(rears)
                self.speak(f"Rear tyres overheating at {avg} degrees. Smooth throttle on corner exit.", Priority.NORMAL)
            self.tyre_state.last_alert_time = now

    # ──────────────────────────────────────────
    # Braking Point Callouts
    # ──────────────────────────────────────────

    def check_braking_points(self, lap: LapData, telemetry: CarTelemetryData):
        if not self.braking_points or telemetry.speed < 60:
            return

        dist = lap.lap_distance
        if dist < 50:
            # Clear announcements near start/finish
            self.announced_braking.clear()
            return

        for bp_dist, corner_name, message in self.braking_points:
            approach_dist = bp_dist - dist
            if 0 < approach_dist <= BRAKING_WARN_DISTANCE:
                if corner_name not in self.announced_braking:
                    self.announced_braking.add(corner_name)
                    dist_rnd = int(round(approach_dist / 10.0) * 10)
                    self.speak(f"{message}, {dist_rnd} metres.", Priority.CRITICAL)

    # ──────────────────────────────────────────
    # Corner Diagnostic Engine ("Why You Are Slower")
    # ──────────────────────────────────────────

    def update_corners(self, telemetry: CarTelemetryData, lap: LapData):
        """Track apex speeds, braking points and exit speeds for each corner."""
        dist = lap.lap_distance
        speed = telemetry.speed
        brake = telemetry.brake

        for c in self.corners:
            c_name = c["name"]
            c_start = c["start"]
            c_end = c["end"]

            if c_start <= dist <= c_end:
                if c_name not in self.current_corner_data:
                    self.current_corner_data[c_name] = {
                        "min_speed": speed,
                        "brake_point": None,
                        "start_time_ms": lap.current_lap_time_ms,
                        "end_time_ms": None,
                    }

                data = self.current_corner_data[c_name]
                if speed < data["min_speed"]:
                    data["min_speed"] = speed

                if brake > 0.3 and data["brake_point"] is None:
                    data["brake_point"] = int(dist)

            elif dist > c_end and c_name in self.current_corner_data:
                data = self.current_corner_data[c_name]
                if data["end_time_ms"] is None:
                    data["end_time_ms"] = lap.current_lap_time_ms
                    self._diagnose_corner(c_name, data, c)

    def _diagnose_corner(self, c_name: str, current_data: dict, ref_def: dict):
        """Diagnose time loss in corner and update HUD."""
        start_t = current_data.get("start_time_ms", 0)
        end_t = current_data.get("end_time_ms", 0)
        curr_dur = (end_t - start_t) / 1000.0 if end_t and start_t else 0.0

        ref_apex = ref_def["ref_apex"]
        ref_brake = ref_def["ref_brake"]

        curr_apex = current_data.get("min_speed", 0)
        curr_brake = current_data.get("brake_point", ref_brake)

        # Baseline comparison
        if c_name in self.best_corner_data:
            best_d = self.best_corner_data[c_name]
            best_apex = best_d["min_speed"]
            best_dur = (best_d["end_time_ms"] - best_d["start_time_ms"]) / 1000.0 if best_d.get("end_time_ms") else curr_dur
            delta_s = curr_dur - best_dur
        else:
            best_apex = ref_apex
            delta_s = max(0.0, (ref_apex - curr_apex) * 0.02)

        # Diagnosis string
        advice = []
        if curr_brake and curr_brake < (ref_brake - 20):
            diff = ref_brake - curr_brake
            advice.append(f"Braked {diff}m too early before entry.")
        if curr_apex < (best_apex - 8):
            diff = best_apex - curr_apex
            advice.append(f"Apex speed {diff} km/h slower than reference.")
        elif curr_apex >= best_apex:
            advice.append("Good apex speed maintained!")

        if not advice:
            advice_text = "Good execution through corner."
        else:
            advice_text = " ".join(advice)

        # Update HUD corner list
        diag_entry = {
            "name": c_name,
            "delta": delta_s,
            "current_apex": curr_apex,
            "best_apex": best_apex,
            "brake_point": curr_brake or "Lift",
            "advice": advice_text,
        }

        # Keep latest corner diagnostics
        existing_idx = next((i for i, item in enumerate(self.corner_diagnostics) if item["name"] == c_name), None)
        if existing_idx is not None:
            self.corner_diagnostics[existing_idx] = diag_entry
        else:
            self.corner_diagnostics.append(diag_entry)

    # ──────────────────────────────────────────
    # Lap Delta Tracker & Sector Reporting
    # ──────────────────────────────────────────

    def update_delta(self, lap: LapData, telemetry: CarTelemetryData):
        now = time.time()
        dist = lap.lap_distance
        elapsed_ms = lap.current_lap_time_ms

        if dist < 0 or elapsed_ms <= 0:
            return

        # New lap check
        if lap.current_lap_num != self.delta.current_lap_num:
            self._on_new_lap(lap)

        # Sector reporting (Sector 0 -> 1 -> 2)
        if lap.sector != self.last_sector:
            self._on_sector_change(lap)
            self.last_sector = lap.sector

        # Sample at regular distance intervals
        if dist - self.delta.last_sample_distance >= DELTA_SAMPLE_INTERVAL:
            self.delta.last_sample_distance = dist
            key = round(dist / DELTA_SAMPLE_INTERVAL) * DELTA_SAMPLE_INTERVAL
            self.delta.current_lap_times[key] = elapsed_ms
            self.delta.current_lap_speeds.append([round(dist, 1), telemetry.speed])

            # Calculate live delta if baseline exists
            if self.delta.best_lap_times and key in self.delta.best_lap_times:
                delta_ms = elapsed_ms - self.delta.best_lap_times[key]
                self.delta.last_reported_delta_ms = delta_ms

                # Voice delta callout periodically
                if now - self.delta.last_delta_report_time >= DELTA_REPORT_INTERVAL:
                    self.delta.last_delta_report_time = now
                    delta_s = abs(delta_ms) / 1000.0
                    if delta_ms < -100:
                        self.speak(f"Minus {delta_s:.1f} seconds to your best. Strong pace.", Priority.LOW)
                    elif delta_ms > 150:
                        self.speak(f"Plus {delta_s:.1f} seconds to your best.", Priority.LOW)

    def _on_sector_change(self, lap: LapData):
        """Announce sector timing and delta."""
        if lap.sector == 1 and lap.sector1_time_ms > 0:
            sec_s = lap.sector1_time_ms / 1000.0
            self.speak(f"Sector 1: {sec_s:.1f} seconds.", Priority.LOW)
        elif lap.sector == 2 and lap.sector2_time_ms > 0:
            sec_s = lap.sector2_time_ms / 1000.0
            self.speak(f"Sector 2: {sec_s:.1f} seconds.", Priority.LOW)

    def _on_new_lap(self, lap: LapData):
        """Handle lap completion and save best baseline."""
        prev_lap_num = self.delta.current_lap_num
        self.delta.current_lap_num = lap.current_lap_num
        self.announced_braking.clear()

        # If previous lap completed with valid lap time
        if prev_lap_num > 0 and lap.last_lap_time_ms > 0 and self.delta.current_lap_times:
            last_ms = lap.last_lap_time_ms
            secs = last_ms / 1000.0
            mins = int(secs // 60)
            secs_rem = secs % 60

            # Store as best if first completed lap or faster
            is_best = (self.delta.best_lap_time_ms == 0 or last_ms < self.delta.best_lap_time_ms)

            if is_best:
                self.delta.best_lap_times = dict(self.delta.current_lap_times)
                self.delta.best_lap_speeds = list(self.delta.current_lap_speeds)
                self.delta.best_lap_time_ms = last_ms
                self.delta.best_lap_num = prev_lap_num
                self.best_corner_data = dict(self.current_corner_data)

                self.speak(f"Personal best! {mins} minute {secs_rem:.3f}. New reference lap set.", Priority.HIGH)
            else:
                diff_s = (last_ms - self.delta.best_lap_time_ms) / 1000.0
                self.speak(f"Lap complete: {mins} {secs_rem:.3f}. Plus {diff_s:.2f} seconds to your best.", Priority.NORMAL)

        # Reset current recording lap
        self.delta.current_lap_times.clear()
        self.delta.current_lap_speeds.clear()
        self.delta.last_sample_distance = -999.0
        self.delta.current_lap_invalid = False
        self.current_corner_data.clear()

    # ──────────────────────────────────────────
    # Main Update
    # ──────────────────────────────────────────

    def update_telemetry(self, telemetry: CarTelemetryData, lap: LapData):
        """Main update called on each telemetry packet."""
        self.analyze_tyres(telemetry, lap)
        self.check_braking_points(lap, telemetry)
        self.update_corners(telemetry, lap)
        self.update_delta(lap, telemetry)

        # Stream snapshot to Web HUD
        update_web_state({
            "connected": True,
            "track_name": self.track_name,
            "track_id": self.track_id,
            "speed": telemetry.speed,
            "gear": telemetry.gear,
            "rpm": telemetry.engine_rpm,
            "drs": bool(telemetry.drs),
            "throttle": round(telemetry.throttle, 2),
            "brake": round(telemetry.brake, 2),
            "tyre_surface_temps": list(telemetry.tyres_surface_temperature),
            "tyre_inner_temps": list(telemetry.tyres_inner_temperature),
            "tyre_pressures": list(telemetry.tyres_pressure),
            "engine_temp": telemetry.engine_temperature,
            "lap_num": lap.current_lap_num,
            "position": lap.car_position,
            "lap_time_ms": lap.current_lap_time_ms,
            "last_lap_time_ms": lap.last_lap_time_ms,
            "best_lap_time_ms": self.delta.best_lap_time_ms,
            "delta_ms": self.delta.last_reported_delta_ms,
            "lap_distance": round(lap.lap_distance, 1),
            "sector": lap.sector,
            "corner_analysis": self.corner_diagnostics,
            "speed_trace_current": self.delta.current_lap_speeds[-120:],
            "speed_trace_best": self.delta.best_lap_speeds
        })
