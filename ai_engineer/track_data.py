"""
Track Database — Braking Points & Setup Recommendations
=========================================================
Per-track data for:
  • Braking points: (distance_m, corner_name, braking_zone_start)
  • Setup baseline recommendations (tyre pressure, camber, etc.)

Distances are in metres from the start/finish line (matching lapDistance in telemetry).
"""

# ──────────────────────────────────────────────
# Braking Point Format:
#   (distance_metres, corner_name, advisory_message)
#
# These are approximate braking points for 100% AI difficulty.
# The system will call out "Brake in 100 metres for Turn X" when
# the player's lapDistance approaches (distance - 100m).
# ──────────────────────────────────────────────

BRAKING_POINTS: dict[int, list[tuple[float, str, str]]] = {
    # Track ID 3: Bahrain International Circuit (5.412 km)
    3: [
        (410,   "Turn 1",  "Heavy braking zone, turn 1"),
        (780,   "Turn 4",  "Brake for turn 4, second gear"),
        (1290,  "Turn 6",  "Brake hard for turn 6"),
        (1670,  "Turn 8",  "Lift and brake for turn 8"),
        (2050,  "Turn 10", "Heavy braking, turn 10"),
        (2890,  "Turn 11", "Brake for turn 11"),
        (3500,  "Turn 13", "Short braking zone, turn 13"),
        (4150,  "Turn 14", "Brake for the hairpin, turn 14"),
    ],

    # Track ID 7: Silverstone (5.891 km)
    7: [
        (290,   "Turn 1 Abbey",       "Brake for Abbey"),
        (850,   "Turn 3 Village",     "Lift and brake for Village"),
        (1180,  "Turn 6 Brooklands",  "Brake for Brooklands"),
        (1680,  "Turn 7 Luffield",    "Brake for Luffield"),
        (2600,  "Turn 9 Copse",       "Light braking into Copse"),
        (3400,  "Maggots-Becketts",    "Lift through Maggots and Becketts"),
        (4250,  "Turn 14 Chapel",     "Flat if you can, Chapel"),
        (4950,  "Turn 15 Stowe",      "Heavy braking into Stowe"),
        (5400,  "Turn 16 Club",       "Brake for Club"),
    ],

    # Track ID 11: Monza (5.793 km)
    11: [
        (340,   "Turn 1 Variante",    "Heavy braking, first chicane"),
        (1230,  "Turn 4 Curva Grande", "Light braking for Curva Grande exit"),
        (1950,  "Turn 4-5 Variante della Roggia", "Hard brake for second chicane"),
        (3550,  "Lesmo 1",            "Brake for Lesmo 1"),
        (3950,  "Lesmo 2",            "Brake for Lesmo 2"),
        (4700,  "Ascari",             "Brake for Ascari chicane"),
        (5350,  "Parabolica",         "Brake for Parabolica"),
    ],

    # Track ID 10: Spa-Francorchamps (7.004 km)
    10: [
        (250,   "La Source",           "Heavy braking for La Source hairpin"),
        (1800,  "Les Combes",          "Brake hard for Les Combes"),
        (2400,  "Rivage",              "Brake for Rivage"),
        (4100,  "Pouhon",              "Lift for Pouhon, full commitment"),
        (4750,  "Fagnes",              "Light braking for Fagnes chicane"),
        (5200,  "Stavelot",            "Brake for Stavelot"),
        (6050,  "Bus Stop",            "Heavy braking for Bus Stop chicane"),
    ],

    # Track ID 4: Catalunya (4.675 km)
    4: [
        (320,   "Turn 1",    "Brake hard for Turn 1"),
        (750,   "Turn 3",    "Lift and brake for Turn 3"),
        (1200,  "Turn 5",    "Brake for Turn 5, long right-hander"),
        (1780,  "Turn 7",    "Lift for Turn 7"),
        (2350,  "Turn 9",    "Short braking zone, Turn 9"),
        (2950,  "Turn 10",   "Brake for Turn 10 hairpin"),
        (3700,  "Turn 12",   "Lift for Turn 12"),
        (4200,  "Turn 14",   "Brake for the final chicane"),
    ],

    # Track ID 5: Monaco (3.337 km)
    5: [
        (180,   "Sainte Devote",  "Brake for Sainte Devote"),
        (720,   "Massenet",       "Light braking for Massenet"),
        (980,   "Casino",         "Brake for Casino Square"),
        (1200,  "Mirabeau",       "Hard braking for Mirabeau"),
        (1380,  "Grand Hotel Hairpin", "Heavy braking, hairpin"),
        (2050,  "Nouvelle Chicane", "Brake for the chicane"),
        (2700,  "Tabac",          "Light braking for Tabac"),
        (2950,  "Swimming Pool",  "Quick braking for the Swimming Pool"),
        (3250,  "Rascasse",       "Brake for Rascasse"),
    ],

    # Track ID 14: Abu Dhabi - Yas Marina (5.281 km)
    14: [
        (350,   "Turn 1",    "Brake hard for Turn 1"),
        (850,   "Turn 5",    "Brake for Turn 5"),
        (1500,  "Turn 6",    "Lift and brake for Turn 6"),
        (2100,  "Turn 7",    "Brake for Turn 7"),
        (2800,  "Turn 8-9",  "Brake for the chicane"),
        (3500,  "Turn 11",   "Heavy braking for Turn 11"),
        (4300,  "Turn 14",   "Brake for Turn 14"),
        (4900,  "Turn 17-18", "Brake for the final corners"),
    ],

    # Track ID 17: Red Bull Ring (4.318 km)
    17: [
        (300,   "Turn 1",   "Brake hard for Turn 1"),
        (850,   "Turn 2",   "Light braking for Turn 2"),
        (1450,  "Turn 3",   "Brake for Turn 3"),
        (2200,  "Turn 4",   "Hard braking for Turn 4"),
        (3450,  "Turn 6",   "Lift for Turn 6"),
        (3900,  "Turn 7",   "Lift for Turn 7"),
    ],

    # Track ID 6: Montreal - Circuit Gilles Villeneuve (4.361 km)
    6: [
        (350,   "Turn 1-2",   "Brake for the first chicane"),
        (900,   "Turn 3",     "Brake for Turn 3"),
        (1500,  "Turn 5",     "Short braking for Turn 5"),
        (1900,  "Turn 6",     "Brake for Turn 6 hairpin"),
        (2750,  "Turn 8-9",   "Brake for chicane"),
        (3500,  "Turn 10",    "Brake for Turn 10"),
        (4100,  "Turn 13-14", "Heavy braking for the final chicane, Wall of Champions"),
    ],

    # Track ID 20: Baku City Circuit (6.003 km)
    20: [
        (450,   "Turn 1",     "Brake for Turn 1"),
        (1100,  "Turn 3",     "Brake for Turn 3"),
        (2700,  "Turn 7",     "Brake for Turn 7"),
        (3200,  "Turn 8",     "Light braking for the castle section"),
        (4150,  "Turn 12",    "Brake for Turn 12"),
        (4600,  "Turn 15",    "Heavy braking for Turn 15"),
        (5400,  "Turn 16",    "Brake for Turn 16"),
    ],

    # Track ID 26: Zandvoort (4.259 km)
    26: [
        (300,   "Tarzanbocht",  "Brake for Tarzan corner"),
        (900,   "Turn 3",      "Brake for Turn 3"),
        (1500,  "Turn 7",      "Lift for Turn 7"),
        (2000,  "Turn 9",      "Brake for Turn 9"),
        (2700,  "Turn 11",     "Brake for Turn 11"),
        (3500,  "Turn 13",     "Brake for Turn 13"),
        (3900,  "Arie Luyendyk", "Banking entry, manage the speed"),
    ],

    # Track ID 27: Imola (4.909 km)
    27: [
        (300,   "Tamburello",   "Brake for Tamburello chicane"),
        (1050,  "Tosa",         "Brake for Tosa"),
        (1800,  "Piratella",    "Brake for Piratella"),
        (2300,  "Acque Minerali", "Brake for Acque Minerali"),
        (3300,  "Variante Alta", "Brake for Variante Alta"),
        (4100,  "Rivazza 1",    "Brake for Rivazza"),
        (4500,  "Rivazza 2",    "Brake for Rivazza 2"),
    ],

    # Track ID 29: Jeddah (6.174 km)
    29: [
        (450,   "Turn 1",     "Brake for Turn 1"),
        (1350,  "Turn 4",     "Brake for Turn 4"),
        (2500,  "Turn 10",    "Brake for Turn 10"),
        (3400,  "Turn 13",    "Heavy braking for Turn 13"),
        (4200,  "Turn 17",    "Brake for Turn 17"),
        (5000,  "Turn 22",    "Brake for Turn 22"),
        (5700,  "Turn 25",    "Brake for Turn 25"),
        (6000,  "Turn 27",    "Final corner, light braking"),
    ],

    # Track ID 16: Interlagos (4.309 km)
    16: [
        (280,   "Turn 1 Senna S",  "Brake for Senna S"),
        (700,   "Turn 3",          "Brake for Turn 3 Curva do Sol"),
        (1400,  "Turn 4",          "Brake for Turn 4 Descida do Lago"),
        (2100,  "Turn 6",          "Brake for Turn 6"),
        (2700,  "Turn 8",          "Brake for Turn 8 hairpin"),
        (3200,  "Turn 10",         "Lift for Turn 10"),
        (3900,  "Turn 12 Junção",  "Brake for Junção"),
    ],

    # Track ID 13: Suzuka (5.807 km)
    13: [
        (300,   "Turn 1",         "Brake for Turn 1"),
        (1050,  "Turn 3 Esses",   "Lift through the Esses"),
        (1700,  "Dunlop",         "Brake for Dunlop curve"),
        (2300,  "Degner 1",       "Brake for Degner"),
        (2700,  "Degner 2",       "Short braking, Degner 2"),
        (3100,  "Hairpin",        "Heavy braking for the hairpin"),
        (3900,  "Spoon",          "Brake for Spoon curve"),
        (4800,  "130R",           "Flat if brave, 130R"),
        (5300,  "Casio Triangle",  "Heavy braking for the chicane"),
    ],

    # Track ID 15: Austin COTA (5.513 km)
    15: [
        (350,   "Turn 1",    "Heavy braking uphill into Turn 1"),
        (1050,  "Turn 4",    "Brake for Turn 4"),
        (1600,  "Turn 7",    "Brake for Turn 7"),
        (2000,  "Turn 8",    "Brake for Turn 8"),
        (2700,  "Turn 11",   "Brake for Turn 11 hairpin"),
        (3200,  "Turn 12",   "Hard braking, Turn 12"),
        (4100,  "Turn 15",   "Brake for Turn 15"),
        (4900,  "Turn 18",   "Brake for Turn 18"),
        (5200,  "Turn 19",   "Brake for Turn 19"),
    ],

    # Track ID 19: Mexico City (4.304 km)
    19: [
        (350,   "Turn 1",     "Brake hard for Turn 1"),
        (800,   "Turn 4",     "Brake for Turn 4"),
        (1400,  "Turn 6",     "Lift for Turn 6"),
        (1900,  "Turn 7",     "Brake for Turn 7"),
        (2450,  "Turn 9",     "Brake for Turn 9"),
        (3050,  "Turn 11",    "Short braking, Turn 11"),
        (3500,  "Turn 12",    "Brake for Peraltada entry"),
        (4050,  "Turn 16",    "Brake for the stadium section"),
    ],

    # Track ID 12: Singapore (5.063 km)
    12: [
        (350,   "Turn 1",     "Brake hard for Turn 1"),
        (700,   "Turn 3",     "Brake for Turn 3"),
        (1050,  "Turn 5",     "Brake for Turn 5"),
        (1400,  "Turn 7",     "Brake for Turn 7"),
        (1900,  "Turn 8",     "Lift for Turn 8"),
        (2300,  "Turn 10",    "Brake for Turn 10"),
        (2700,  "Turn 11",    "Brake for Turn 11"),
        (3200,  "Turn 13",    "Light braking for Turn 13"),
        (3700,  "Turn 14",    "Brake for Turn 14"),
        (4300,  "Turn 16-17", "Brake for Turn 16"),
        (4650,  "Turn 18-19", "Brake for the final turns"),
    ],

    # Track ID 9: Hungaroring (4.381 km)
    9: [
        (300,   "Turn 1",   "Brake hard for Turn 1"),
        (750,   "Turn 2",   "Brake for Turn 2"),
        (1200,  "Turn 4",   "Brake for Turn 4"),
        (1650,  "Turn 6",   "Lift for Turn 6"),
        (2200,  "Turn 8",   "Brake for Turn 8"),
        (2700,  "Turn 9",   "Brake for Turn 9"),
        (3200,  "Turn 11",  "Brake for Turn 11"),
        (3700,  "Turn 12",  "Short braking, Turn 12"),
        (4050,  "Turn 14",  "Brake for the final chicane"),
    ],

    # Track ID 18: Sochi (5.848 km)
    18: [
        (450,   "Turn 2",   "Brake for Turn 2"),
        (1300,  "Turn 3",   "Brake for Turn 3"),
        (1900,  "Turn 4",   "Brake for Turn 4"),
        (2800,  "Turn 7",   "Brake for Turn 7"),
        (3400,  "Turn 8",   "Light braking for Turn 8"),
        (4100,  "Turn 10",  "Brake for Turn 10"),
        (4600,  "Turn 13",  "Brake for Turn 13"),
        (5200,  "Turn 14",  "Brake for Turn 14"),
        (5600,  "Turn 16",  "Brake for Turn 16"),
    ],

    # Track ID 28: Portimão (4.653 km)
    28: [
        (350,   "Turn 1",   "Brake for Turn 1"),
        (900,   "Turn 3",   "Brake for Turn 3"),
        (1500,  "Turn 5",   "Brake for Turn 5"),
        (2100,  "Turn 7",   "Brake for Turn 7"),
        (2900,  "Turn 9",   "Brake for Turn 9"),
        (3400,  "Turn 11",  "Brake for Turn 11"),
        (4000,  "Turn 13",  "Brake for Turn 13"),
        (4350,  "Turn 14",  "Brake for Turn 14, final corner"),
    ],
}


# ──────────────────────────────────────────────
# Setup Recommendations per Track
# ──────────────────────────────────────────────
# Baseline advice keyed by track ID.
# These are general guidelines that the engineer will mention
# when temps go out of range.

SETUP_ADVICE: dict[int, dict] = {
    # Default baseline for any track not specifically listed
    -1: {
        "front_wing": "Medium downforce",
        "rear_wing": "Medium downforce",
        "front_camber": "-3.00°",
        "rear_camber": "-1.50°",
        "front_toe": "0.07°",
        "rear_toe": "0.20°",
        "front_suspension": "5",
        "rear_suspension": "3",
        "front_anti_roll": "6",
        "rear_anti_roll": "4",
        "front_ride_height": "3",
        "rear_ride_height": "5",
        "brake_pressure": "90%",
        "brake_bias": "56%",
        "front_tyre_pressure": "23.5 PSI",
        "rear_tyre_pressure": "22.0 PSI",
        "notes": "Balanced baseline setup — adjust wings for track character."
    },

    # Monza – Low downforce temple of speed
    11: {
        "front_wing": "Low downforce (1-3)",
        "rear_wing": "Low downforce (1-3)",
        "front_camber": "-2.50°",
        "rear_camber": "-1.00°",
        "brake_pressure": "95%",
        "brake_bias": "58%",
        "front_tyre_pressure": "24.0 PSI",
        "rear_tyre_pressure": "22.5 PSI",
        "notes": "Trim the wings. Monza is about top speed. High brake pressure for heavy stops."
    },

    # Monaco – Maximum downforce
    5: {
        "front_wing": "High downforce (8-10)",
        "rear_wing": "High downforce (8-10)",
        "front_camber": "-3.50°",
        "rear_camber": "-2.00°",
        "brake_pressure": "85%",
        "brake_bias": "54%",
        "front_tyre_pressure": "22.5 PSI",
        "rear_tyre_pressure": "21.5 PSI",
        "notes": "Max downforce. Softer brakes, you need rotation. Lower pressures help warm-up."
    },

    # Spa – Medium-high downforce
    10: {
        "front_wing": "Medium-high downforce (5-7)",
        "rear_wing": "Medium-high downforce (6-8)",
        "front_camber": "-3.00°",
        "rear_camber": "-1.50°",
        "brake_pressure": "92%",
        "brake_bias": "56%",
        "front_tyre_pressure": "23.5 PSI",
        "rear_tyre_pressure": "22.0 PSI",
        "notes": "Balance speed on Kemmel straight with grip in sector 2. Watch tyre temps in Pouhon."
    },

    # Silverstone – Medium downforce
    7: {
        "front_wing": "Medium downforce (5-6)",
        "rear_wing": "Medium downforce (5-7)",
        "front_camber": "-3.20°",
        "rear_camber": "-1.50°",
        "brake_pressure": "90%",
        "brake_bias": "55%",
        "front_tyre_pressure": "23.0 PSI",
        "rear_tyre_pressure": "22.0 PSI",
        "notes": "High-speed corners demand good aero balance. Front-limited through Maggots-Becketts."
    },

    # Bahrain
    3: {
        "front_wing": "Medium downforce (4-6)",
        "rear_wing": "Medium downforce (5-7)",
        "front_camber": "-3.00°",
        "rear_camber": "-1.50°",
        "brake_pressure": "92%",
        "brake_bias": "56%",
        "front_tyre_pressure": "23.5 PSI",
        "rear_tyre_pressure": "22.0 PSI",
        "notes": "Rear traction is key out of slow corners. Watch rear tyre temperatures closely."
    },

    # Red Bull Ring – Low-medium downforce
    17: {
        "front_wing": "Low-medium downforce (3-5)",
        "rear_wing": "Low-medium downforce (4-6)",
        "front_camber": "-2.80°",
        "rear_camber": "-1.20°",
        "brake_pressure": "93%",
        "brake_bias": "57%",
        "front_tyre_pressure": "24.0 PSI",
        "rear_tyre_pressure": "22.5 PSI",
        "notes": "Short track with elevation. Good traction out of Turn 4 is crucial."
    },
}


def get_braking_points(track_id: int) -> list[tuple[float, str, str]]:
    """Get braking points for a track. Returns empty list if track not mapped."""
    return BRAKING_POINTS.get(track_id, [])


def get_setup_advice(track_id: int) -> dict:
    """Get setup advice for a track. Falls back to default baseline."""
    return SETUP_ADVICE.get(track_id, SETUP_ADVICE[-1])
