from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum

class GangColor(Enum):
    RED = "🔴"
    BLUE = "🔵"
    GREEN = "🟢"
    YELLOW = "🟡"
    PURPLE = "🟣"
    ORANGE = "🟠"

@dataclass
class GangMember:
    user_id: int
    username: str
    gang_name: str
    rank: str = "Soldier"
    xp: int = 0
    coins: int = 100
    respect: int = 0
    wins: int = 0
    losses: int = 0
    joined_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_war_time: Optional[str] = None
    last_daily_bonus: Optional[str] = None
    territory_contributions: int = 0
    attack_count: int = 0

@dataclass
class Gang:
    name: str
    color: str
    leader_id: int
    territory: int = 1
    total_xp: int = 0
    total_coins: int = 0
    total_respect: int = 0
    wins: int = 0
    losses: int = 0
    members: List[int] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    territory_control: Dict[str, int] = field(default_factory=dict)
    total_ranking_points: int = 0

@dataclass
class War:
    id: str
    attacker_gang: str
    defender_gang: str
    attacker_score: int = 0
    defender_score: int = 0
    status: str = "active"
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    ended_at: Optional[str] = None
    participants: List[int] = field(default_factory=list)
    rewards_claimed: bool = False
    winner: Optional[str] = None

@dataclass
class Territory:
    name: str
    controlling_gang: Optional[str] = None
    value: int = 1
    defense_bonus: int = 0
    loot_multiplier: float = 1.0
