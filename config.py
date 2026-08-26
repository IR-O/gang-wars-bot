import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN', '8913022550:AAEbnERs-UtXKf2PSQphO5M0cmwGCk1SCb8')

# Fix: Properly parse ADMIN_IDS
admin_ids_str = os.getenv('ADMIN_IDS', '')
if admin_ids_str:
    ADMIN_IDS = [int(id.strip()) for id in admin_ids_str.split(',') if id.strip()]
else:
    ADMIN_IDS = [8437795303]  # Default admin ID

DATA_FILE = os.getenv('DATA_FILE', 'data/gang_wars_data.json')
PORT = int(os.getenv('PORT', 5000))

# Game Configuration
WAR_WIN_SCORE = 5
ATTACK_COOLDOWN = 30  # seconds
WAR_START_COOLDOWN = 1800  # 30 minutes
DAILY_BONUS_COOLDOWN = 86400  # 24 hours
MAX_MEMBERS_PER_GANG = 50
MIN_GANG_MEMBERS_FOR_WAR = 2

# Reward Configuration
XP_PER_ATTACK_WIN = (5, 20)
XP_PER_ATTACK_LOSS = (3, 10)
COINS_PER_ATTACK_WIN = (10, 50)
RESPECT_PER_ATTACK = (1, 5)
DAILY_BONUS_COINS = (20, 80)
DAILY_BONUS_XP = (10, 40)
DAILY_BONUS_RESPECT = (1, 3)

# Rank Configuration
RANKS = {
    0: "Recruit",
    50: "Soldier",
    200: "Veteran",
    500: "Elite",
    1000: "Captain",
    2000: "Commander",
    5000: "Warlord",
    10000: "Legend"
}

# Territories
TERRITORIES = [
    {"name": "Warehouse District", "value": 2, "defense_bonus": 1, "loot_multiplier": 1.0},
    {"name": "Financial Plaza", "value": 3, "defense_bonus": 2, "loot_multiplier": 1.2},
    {"name": "Industrial Zone", "value": 4, "defense_bonus": 2, "loot_multiplier": 1.1},
    {"name": "Downtown Core", "value": 5, "defense_bonus": 3, "loot_multiplier": 1.5},
    {"name": "Harbor Area", "value": 3, "defense_bonus": 1, "loot_multiplier": 1.0},
    {"name": "University Campus", "value": 2, "defense_bonus": 0, "loot_multiplier": 0.8},
    {"name": "Shopping Mall", "value": 3, "defense_bonus": 1, "loot_multiplier": 1.1},
    {"name": "Government District", "value": 6, "defense_bonus": 4, "loot_multiplier": 1.8},
    {"name": "Airport Area", "value": 4, "defense_bonus": 2, "loot_multiplier": 1.3},
]

# Available Colors
AVAILABLE_COLORS = ["🔴", "🔵", "🟢", "🟡", "🟣", "🟠"]
COLOR_NAMES = {
    "🔴": "RED",
    "🔵": "BLUE",
    "🟢": "GREEN",
    "🟡": "YELLOW",
    "🟣": "PURPLE",
    "🟠": "ORANGE"
}
