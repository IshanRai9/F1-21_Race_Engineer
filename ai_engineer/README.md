# F1 2021 AI Race Engineer

> An intelligent real-time race engineer that reads your F1 2021 telemetry and talks to you like a real pit wall.

## Quick Start

### 1. Install Dependencies
```bash
cd ai_engineer
pip install -r requirements.txt
```

### 2. Configure F1 2021
In-game: **Settings → Telemetry**
| Setting | Value |
|---------|-------|
| UDP Telemetry | **ON** |
| UDP Broadcast | **ON** |
| UDP IP Address | `127.0.0.1` |
| UDP Port | `20777` |
| UDP Format | `2021` |

### 3. Run the Engineer
```bash
python main.py
```

Then start a session in F1 2021. The engineer will speak!

## Command Line Options
```
python main.py [--port 20777] [--no-voice] [--debug] [--voice-rate 175] [--voice-index 0]
```

| Flag | Description |
|------|-------------|
| `--port` | UDP port (default: 20777) |
| `--no-voice` | Console-only mode, no TTS |
| `--debug` | Show packet parsing errors |
| `--voice-rate` | Speech speed in WPM (default: 175) |
| `--voice-index` | Select system voice by index |

## What It Does

### 🗣️ Voice Callouts
- **Braking points** — "Brake for Turn 1, 120 metres" 
- **Tyre temperatures** — "Front tyres overheating at 108 degrees"
- **Lap deltas** — "You're 0.3 seconds faster than your best"
- **Position changes** — "Position gained! You're now P3"
- **Lap times** — "Personal best! 1 minute 29.432"
- **Setup advice** — "Consider lowering front tyre pressure"

### 📊 Live Console Dashboard
- Speed, gear, RPM, DRS status
- Throttle & brake bars
- Tyre surface temperatures (all 4 corners)
- Tyre pressures & engine temperature
- Current lap time and delta to best

### 🏁 Tracks with Braking Data
Bahrain, Silverstone, Monza, Spa, Catalunya, Monaco, Abu Dhabi, Red Bull Ring,
Montreal, Baku, Zandvoort, Imola, Jeddah, Interlagos, Suzuka, COTA, Mexico City,
Singapore, Hungaroring, Sochi, Portimão

## Architecture

```
ai_engineer/
├── main.py          # UDP listener + console dashboard
├── packets.py       # F1 2021 packet struct definitions  
├── analysis.py      # Tyre/braking/delta/position analysis
├── voice_engine.py  # Threaded TTS with rate limiting
├── track_data.py    # Braking points + setup advice per track
└── requirements.txt # pip dependencies
```

**Zero game files are modified.** The engineer is a standalone application that reads the game's UDP telemetry broadcast.
