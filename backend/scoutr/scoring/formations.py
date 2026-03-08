"""Formation profiles for tactical compatibility scoring.

Maps each formation to required pressing intensity, width, and ball-progression
style. Used to produce formation_compatibility scores (0-100 per formation).
"""

FORMATION_PROFILES = {
    "4-3-3": {
        "description": "High-pressing, wide, possession-based",
        "pressing_intensity": "high",  # PPDA target: < 10
        "ppda_max": 12.0,
        "ppda_ideal": 8.0,
        "pressure_success_min": 0.32,
        "width": "wide",
        "ball_progression": "high",
        "progressive_carries_min": 2.0,
    },
    "4-2-3-1": {
        "description": "Counter-press, compact in defense, quick transitions",
        "pressing_intensity": "medium_high",
        "ppda_max": 14.0,
        "ppda_ideal": 10.0,
        "pressure_success_min": 0.28,
        "width": "medium",
        "ball_progression": "medium_high",
        "progressive_carries_min": 1.5,
    },
    "3-5-2": {
        "description": "Wing-back focused, defensive solidity, counter-attack",
        "pressing_intensity": "medium",
        "ppda_max": 16.0,
        "ppda_ideal": 12.0,
        "pressure_success_min": 0.24,
        "width": "wide",
        "ball_progression": "medium",
        "progressive_carries_min": 1.2,
    },
    "4-4-2": {
        "description": "Traditional, compact blocks, direct play",
        "pressing_intensity": "medium",
        "ppda_max": 15.0,
        "ppda_ideal": 11.0,
        "pressure_success_min": 0.26,
        "width": "medium",
        "ball_progression": "medium",
        "progressive_carries_min": 1.0,
    },
    "3-4-3": {
        "description": "Attacking wing-backs, high line, possession",
        "pressing_intensity": "high",
        "ppda_max": 11.0,
        "ppda_ideal": 9.0,
        "pressure_success_min": 0.30,
        "width": "wide",
        "ball_progression": "high",
        "progressive_carries_min": 2.2,
    },
}

# Min defensive actions per 90 expected per position (role-dependent)
DEFENSIVE_ACTIONS_BY_POSITION = {
    "left-back": (6.0, 12.0),   # (min_expected, ideal)
    "right-back": (6.0, 12.0),
    "centre-back": (7.0, 14.0),
    "defensive-midfield": (8.0, 15.0),
    "central-midfield": (4.0, 10.0),
    "attacking-midfield": (2.0, 6.0),
    "winger": (2.0, 6.0),
    "forward": (1.0, 4.0),
}

# Ideal heatmap centroids per position (normalized 0-1: x=width, y=length, y=0 own goal)
HEATMAP_CENTROID_BY_POSITION = {
    "left-back": (0.15, 0.35),
    "right-back": (0.85, 0.35),
    "centre-back": (0.5, 0.2),
    "defensive-midfield": (0.5, 0.35),
    "central-midfield": (0.5, 0.5),
    "attacking-midfield": (0.5, 0.65),
    "winger": (0.25, 0.6),   # left winger; right would be 0.75
    "forward": (0.5, 0.75),
}

# Position-to-formation affinity: which formations suit which positions best
POSITION_FORMATION_WEIGHTS = {
    "left-back": {"4-3-3": 1.2, "3-5-2": 1.1, "3-4-3": 1.2, "4-2-3-1": 1.0, "4-4-2": 0.9},
    "right-back": {"4-3-3": 1.2, "3-5-2": 1.1, "3-4-3": 1.2, "4-2-3-1": 1.0, "4-4-2": 0.9},
    "centre-back": {"3-5-2": 1.2, "3-4-3": 1.1, "4-4-2": 1.1, "4-3-3": 1.0, "4-2-3-1": 1.0},
    "defensive-midfield": {"4-2-3-1": 1.2, "4-3-3": 1.1, "4-4-2": 1.1, "3-5-2": 1.0, "3-4-3": 1.0},
    "central-midfield": {"4-3-3": 1.2, "4-2-3-1": 1.1, "3-5-2": 1.0, "4-4-2": 1.0, "3-4-3": 1.0},
    "attacking-midfield": {"4-2-3-1": 1.2, "4-3-3": 1.1, "3-4-3": 1.0, "3-5-2": 0.9, "4-4-2": 0.9},
    "winger": {"4-3-3": 1.2, "3-4-3": 1.1, "4-2-3-1": 1.1, "4-4-2": 0.9, "3-5-2": 0.9},
    "forward": {"4-4-2": 1.2, "4-3-3": 1.1, "4-2-3-1": 1.0, "3-5-2": 1.0, "3-4-3": 1.0},
}
