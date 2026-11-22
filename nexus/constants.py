RESOURCES = ("wood", "stone", "crystal", "food")
EMOJI = {"wood": "🪵", "stone": "🪨", "crystal": "💎", "food": "🌾"}
LABEL = {"wood": "Wood", "stone": "Stone", "crystal": "Crystal", "food": "Food"}

STRUCTURES = {
    "outpost": {"name": "Frontier Outpost", "description": "A foothold for future exploration.",
                "cost": {"wood": 30, "stone": 20}, "xp": 100},
    "library": {"name": "Grand Library", "description": "A home for shared knowledge.",
                "cost": {"wood": 20, "stone": 15, "crystal": 10}, "xp": 140},
    "greenhouse": {"name": "Sky Greenhouse", "description": "A sustainable source of food.",
                   "cost": {"wood": 15, "stone": 10, "food": 25}, "xp": 120},
}
QUESTS = [
    {"key": "wood", "title": "Forest Steward", "description": "Collect 25 wood as a community.",
     "target": 25, "xp": 80},
    {"key": "stone", "title": "Stonebound", "description": "Collect 20 stone as a community.",
     "target": 20, "xp": 90},
    {"key": "explore", "title": "Beyond the Horizon", "description": "Complete 8 expeditions.",
     "target": 8, "xp": 100},
]
