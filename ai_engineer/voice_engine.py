"""
Voice Engine — The AI Race Engineer's Voice
=============================================
Threaded Text-to-Speech system using pyttsx3.
Runs on a dedicated background thread so speech never blocks telemetry ingestion.

Features:
  • Rate-limiting: same message won't repeat within 30 seconds
  • Priority queue: urgent callouts (braking, overheating) jump the line
  • Non-blocking: main loop calls voice.say() and returns immediately
"""

import threading
import time
import queue
from enum import IntEnum

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None


class Priority(IntEnum):
    LOW = 3       # Informational (delta updates, position)
    NORMAL = 2    # Standard alerts (tyre temps)
    HIGH = 1      # Urgent (critical overheating, rain)
    CRITICAL = 0  # Immediate (braking points)


class VoiceEngine:
    """
    Threaded TTS engine with rate-limiting.

    Usage:
        voice = VoiceEngine()
        voice.start()
        voice.say("Box this lap", priority=Priority.HIGH)
        ...
        voice.shutdown()
    """

    def __init__(self, rate: int = 175, volume: float = 0.9,
                 cooldown_seconds: float = 30.0, voice_index: int = 0):
        """
        Args:
            rate: Speech rate in words-per-minute.
            volume: Volume level 0.0–1.0.
            cooldown_seconds: Minimum interval before repeating the same message.
            voice_index: Index into available system voices (0 = default).
        """
        self._rate = rate
        self._volume = volume
        self._cooldown = cooldown_seconds
        self._voice_index = voice_index

        # Priority queue: (priority, timestamp, message)
        self._queue: queue.PriorityQueue = queue.PriorityQueue()
        self._last_said: dict[str, float] = {}  # message → last_spoken_timestamp
        self._thread: threading.Thread | None = None
        self._running = False
        self._engine_ready = threading.Event()

    def start(self):
        """Start the background TTS thread."""
        if self._thread and self._thread.is_alive():
            return

        self._running = True
        self._thread = threading.Thread(
            target=self._worker,
            name="VoiceEngine",
            daemon=True
        )
        self._thread.start()
        # Wait for engine to initialize
        self._engine_ready.wait(timeout=5.0)

    def _worker(self):
        """Background thread: initialize pyttsx3 and process the speech queue."""
        if pyttsx3 is None:
            print("[VoiceEngine] WARNING: pyttsx3 not installed. Voice disabled.")
            print("[VoiceEngine] Install with: pip install pyttsx3")
            self._engine_ready.set()
            return

        engine = pyttsx3.init()
        engine.setProperty("rate", self._rate)
        engine.setProperty("volume", self._volume)

        # Select voice
        voices = engine.getProperty("voices")
        if voices and self._voice_index < len(voices):
            engine.setProperty("voice", voices[self._voice_index].id)

        self._engine_ready.set()
        print(f"[VoiceEngine] Online. {len(voices)} voice(s) available.")

        while self._running:
            try:
                # Block for up to 0.5s waiting for a message
                priority, _ts, message = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue

            # Rate-limit check
            now = time.time()
            last = self._last_said.get(message, 0.0)
            if now - last < self._cooldown:
                continue

            # Speak
            self._last_said[message] = now
            try:
                engine.say(message)
                engine.runAndWait()
            except Exception as e:
                print(f"[VoiceEngine] TTS error: {e}")

        engine.stop()

    def say(self, message: str, priority: Priority = Priority.NORMAL):
        """
        Queue a message for speech. Non-blocking.

        Args:
            message: Text to speak.
            priority: Speech priority (lower number = higher priority).
        """
        if not self._running:
            return

        # Check rate limit before even queuing
        now = time.time()
        last = self._last_said.get(message, 0.0)
        if now - last < self._cooldown:
            return

        self._queue.put((int(priority), time.time(), message))

    def say_immediate(self, message: str):
        """Queue a message with CRITICAL priority and reset its cooldown."""
        self._last_said.pop(message, None)
        self.say(message, Priority.CRITICAL)

    def shutdown(self):
        """Stop the voice engine gracefully."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
            self._thread = None
        print("[VoiceEngine] Shutdown complete.")

    @property
    def is_running(self) -> bool:
        return self._running and self._thread is not None and self._thread.is_alive()
