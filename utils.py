import random
import time
from datetime import datetime, timedelta
from typing import Tuple, Optional

def get_rank(xp: int) -> str:
    """Get rank based on XP"""
    from config import RANKS
    rank = "Recruit"
    for threshold, rank_name in sorted(RANKS.items(), reverse=True):
        if xp >= threshold:
            rank = rank_name
            break
    return rank

def calculate_attack_power(xp: int, territory_contributions: int) -> int:
    """Calculate attack power based on stats"""
    base = random.randint(1, 20)
    xp_bonus = xp // 50
    territory_bonus = territory_contributions // 10
    return base + xp_bonus + territory_bonus

def calculate_defense_power(gang_members: list, territory_bonus: int) -> int:
    """Calculate defense power for a gang"""
    if not gang_members:
        return random.randint(1, 10)
    
    avg_xp = sum(m.xp for m in gang_members) // len(gang_members)
    base = random.randint(1, 15)
    xp_bonus = avg_xp // 50
    return base + xp_bonus + territory_bonus

def generate_war_id(attacker: str) -> str:
    """Generate unique war ID"""
    timestamp = int(time.time())
    return f"war_{timestamp}_{attacker[:3]}"

def format_time(seconds: int) -> str:
    """Format seconds into human-readable time"""
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes}m {remaining_seconds}s"

def get_territory_defense_bonus(territories: list) -> int:
    """Calculate total defense bonus from territories"""
    return sum(t.defense_bonus for t in territories)

def get_random_loot() -> Tuple[str, int]:
    """Generate random rare loot"""
    loot_items = [
        ("🔫 Rare Weapon", 50),
        ("🛡️ Shield", 40),
        ("💎 Diamond", 100),
        ("📜 Scroll", 30),
        ("⚔️ Sword", 60),
        ("🏹 Bow", 45),
        ("🧪 Potion", 25),
        ("👑 Crown", 200)
    ]
    return random.choice(loot_items)

def is_cooldown_expired(last_time: Optional[str], cooldown_seconds: int) -> Tuple[bool, Optional[int]]:
    """Check if cooldown has expired"""
    if not last_time:
        return True, None
    
    last_attempt = datetime.fromisoformat(last_time)
    elapsed = (datetime.now() - last_attempt).total_seconds()
    
    if elapsed >= cooldown_seconds:
        return True, None
    else:
        remaining = int(cooldown_seconds - elapsed)
        return False, remaining
