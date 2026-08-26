import json
import os
import random
import time
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict, List
import logging

from models import Gang, GangMember, War, Territory, GangColor
from config import *
from utils import *

logger = logging.getLogger(__name__)

class GangWarsGame:
    def __init__(self, data_file=DATA_FILE):
        self.data_file = data_file
        self.gangs: Dict[str, Gang] = {}
        self.members: Dict[int, GangMember] = {}
        self.wars: Dict[str, War] = {}
        self.territories: Dict[str, Territory] = {}
        self.active_wars: Dict[str, War] = {}
        self.cooldowns: Dict[int, Dict[str, float]] = {}
        self.loot_history: List[Dict] = []
        self.load_data()
        
    def load_data(self):
        """Load game data from file"""
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load gangs
                self.gangs = {}
                for name, g_data in data.get('gangs', {}).items():
                    gang = Gang(**g_data)
                    self.gangs[name] = gang
                
                # Load members
                self.members = {}
                for uid, m_data in data.get('members', {}).items():
                    member = GangMember(**m_data)
                    self.members[int(uid)] = member
                
                # Load wars
                self.wars = {}
                for wid, w_data in data.get('wars', {}).items():
                    war = War(**w_data)
                    self.wars[wid] = war
                    if war.status == "active":
                        self.active_wars[wid] = war
                
                # Load territories
                for name, t_data in data.get('territories', {}).items():
                    territory = Territory(**t_data)
                    self.territories[name] = territory
                
                # Load cooldowns
                self.cooldowns = data.get('cooldowns', {})
                # Convert string keys back to int
                self.cooldowns = {int(k): v for k, v in self.cooldowns.items()}
                
                logger.info(f"Loaded {len(self.gangs)} gangs, {len(self.members)} members, {len(self.wars)} wars")
            except Exception as e:
                logger.error(f"Error loading data: {e}")
                self.init_default_data()
        else:
            self.init_default_data()
    
    def init_default_data(self):
        """Initialize with default data"""
        self.gangs = {}
        self.members = {}
        self.wars = {}
        self.active_wars = {}
        self.cooldowns = {}
        self.loot_history = []
        
        # Initialize territories
        self.territories = {}
        for t_data in TERRITORIES:
            territory = Territory(**t_data)
            self.territories[territory.name] = territory
        
        self.save_data()
    
    def save_data(self):
        """Save game data to file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            data = {
                'gangs': {name: gang.__dict__ for name, gang in self.gangs.items()},
                'members': {str(uid): member.__dict__ for uid, member in self.members.items()},
                'wars': {wid: war.__dict__ for wid, war in self.wars.items()},
                'territories': {name: territory.__dict__ for name, territory in self.territories.items()},
                'cooldowns': {str(uid): cooldown for uid, cooldown in self.cooldowns.items()},
                'loot_history': self.loot_history
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    def create_gang(self, user_id: int, username: str, gang_name: str, color: str) -> Tuple[bool, str]:
        """Create a new gang"""
        # Validation
        if gang_name in self.gangs:
            return False, "❌ Gang name already exists!"
        
        if user_id in self.members:
            return False, "❌ You're already in a gang! Leave first."
        
        if len(gang_name) < 2 or len(gang_name) > 20:
            return False, "❌ Gang name must be 2-20 characters!"
        
        if color not in AVAILABLE_COLORS:
            return False, f"❌ Invalid color! Use: {' '.join(AVAILABLE_COLORS)}"
        
        # Check if color is taken
        for g in self.gangs.values():
            if g.color == color:
                return False, "❌ Color already taken!"
        
        # Create gang
        gang = Gang(
            name=gang_name,
            color=color,
            leader_id=user_id,
            members=[user_id]
        )
        self.gangs[gang_name] = gang
        
        # Create member
        member = GangMember(
            user_id=user_id,
            username=username,
            gang_name=gang_name,
            rank="Leader",
            coins=200  # Starting bonus
        )
        self.members[user_id] = member
        
        # Assign default territory
        unclaimed = [t for t in self.territories.values() if t.controlling_gang is None]
        if unclaimed:
            territory = random.choice(unclaimed)
            territory.controlling_gang = gang_name
            gang.territory += territory.value
        
        self.save_data()
        return True, f"✅ {color} Gang '{gang_name}' created successfully!\nYou received a starting bonus of 200 coins!"
    
    def join_gang(self, user_id: int, username: str, gang_name: str) -> Tuple[bool, str]:
        """Join an existing gang"""
        if user_id in self.members:
            return False, "❌ You're already in a gang!"
        
        if gang_name not in self.gangs:
            return False, "❌ Gang doesn't exist!"
        
        gang = self.gangs[gang_name]
        
        if len(gang.members) >= MAX_MEMBERS_PER_GANG:
            return False, f"❌ Gang is full! (Max {MAX_MEMBERS_PER_GANG} members)"
        
        # Add member
        member = GangMember(
            user_id=user_id,
            username=username,
            gang_name=gang_name,
            coins=50  # Joining bonus
        )
        self.members[user_id] = member
        gang.members.append(user_id)
        
        self.save_data()
        return True, f"✅ Joined '{gang_name}' successfully!\nYou received a joining bonus of 50 coins!"
    
    def leave_gang(self, user_id: int) -> Tuple[bool, str]:
        """Leave current gang"""
        if user_id not in self.members:
            return False, "❌ You're not in a gang!"
        
        member = self.members[user_id]
        gang = self.gangs[member.gang_name]
        
        if gang.leader_id == user_id and len(gang.members) > 1:
            return False, "❌ Transfer leadership first or disband the gang!\nUse /transfer <@username>"
        
        # Remove from gang
        gang.members.remove(user_id)
        removed_member = self.members.pop(user_id)
        
        if not gang.members:
            # Delete empty gang and release territories
            for t in self.territories.values():
                if t.controlling_gang == gang.name:
                    t.controlling_gang = None
            del self.gangs[gang.name]
        
        self.save_data()
        return True, f"✅ Left '{gang.name}' successfully!"
    
    def transfer_leadership(self, user_id: int, new_leader_username: str) -> Tuple[bool, str]:
        """Transfer gang leadership"""
        if user_id not in self.members:
            return False, "❌ You're not in a gang!"
        
        member = self.members[user_id]
        gang = self.gangs[member.gang_name]
        
        if gang.leader_id != user_id:
            return False, "❌ Only the leader can transfer leadership!"
        
        # Find new leader
        new_leader_id = None
        for uid, m in self.members.items():
            if m.username.lower() == new_leader_username.lower() and m.gang_name == member.gang_name:
                new_leader_id = uid
                break
        
        if not new_leader_id:
            return False, "❌ Member not found!"
        
        if new_leader_id == user_id:
            return False, "❌ You're already the leader!"
        
        # Transfer leadership
        gang.leader_id = new_leader_id
        member.rank = "Veteran"  # Demote old leader
        self.members[new_leader_id].rank = "Leader"
        
        self.save_data()
        return True, f"✅ Leadership transferred to {new_leader_username}!"
    
    def start_war(self, user_id: int, defender_gang: str) -> Tuple[bool, str]:
        """Start a war between gangs"""
        if user_id not in self.members:
            return False, "❌ You're not in a gang!"
        
        attacker = self.members[user_id]
        attacker_gang = self.gangs[attacker.gang_name]
        
        if attacker.gang_name == defender_gang:
            return False, "❌ Can't attack your own gang!"
        
        if defender_gang not in self.gangs:
            return False, "❌ Defender gang doesn't exist!"
        
        defender_gang_obj = self.gangs[defender_gang]
        
        # Check if attacker is leader or commander
        if attacker.rank not in ["Leader", "Commander", "Warlord", "Legend"]:
            return False, "❌ Only leaders and high-ranking members can start wars!"
        
        if len(attacker_gang.members) < MIN_GANG_MEMBERS_FOR_WAR:
            return False, f"❌ Need at least {MIN_GANG_MEMBERS_FOR_WAR} members to start a war!"
        
        # Check if there's an active war
        for war in self.active_wars.values():
            if war.attacker_gang == attacker.gang_name or war.defender_gang == attacker.gang_name:
                return False, "❌ Your gang is already in a war! Use /warstatus"
            if war.attacker_gang == defender_gang or war.defender_gang == defender_gang:
                return False, "❌ That gang is already in a war!"
        
        # Check cooldown
        if user_id in self.cooldowns:
            if 'war_start' in self.cooldowns[user_id]:
                elapsed = time.time() - self.cooldowns[user_id]['war_start']
                if elapsed < WAR_START_COOLDOWN:
                    remaining = int(WAR_START_COOLDOWN - elapsed)
                    return False, f"❌ War cooldown! Wait {format_time(remaining)}"
        
        # Create war
        war_id = generate_war_id(attacker.gang_name)
        war = War(
            id=war_id,
            attacker_gang=attacker.gang_name,
            defender_gang=defender_gang,
            participants=[user_id]
        )
        self.wars[war_id] = war
        self.active_wars[war_id] = war
        
        # Set cooldown
        if user_id not in self.cooldowns:
            self.cooldowns[user_id] = {}
        self.cooldowns[user_id]['war_start'] = time.time()
        
        self.save_data()
        return True, f"⚔️ WAR STARTED!\n\n{attacker_gang.color} {attacker.gang_name}\nVS\n{defender_gang_obj.color} {defender_gang}\n\nFirst to {WAR_WIN_SCORE} wins!\nUse /warattack to fight!"
    
    def war_attack(self, user_id: int) -> Tuple[bool, str, Optional[Dict]]:
        """Attack in an active war"""
        if user_id not in self.members:
            return False, "❌ You're not in a gang!", None
        
        member = self.members[user_id]
        gang_name = member.gang_name
        
        # Find active war for this gang
        active_war = None
        for war in self.active_wars.values():
            if war.attacker_gang == gang_name or war.defender_gang == gang_name:
                active_war = war
                break
        
        if not active_war:
            return False, "❌ Your gang is not in an active war! Use /startwar", None
        
        # Check attack cooldown
        if user_id in self.cooldowns:
            if 'war_attack' in self.cooldowns[user_id]:
                elapsed = time.time() - self.cooldowns[user_id]['war_attack']
                if elapsed < ATTACK_COOLDOWN:
                    remaining = int(ATTACK_COOLDOWN - elapsed)
                    return False, f"❌ Attack cooldown! Wait {remaining}s", None
        
        # Determine if attacker or defender
        is_attacker = active_war.attacker_gang == gang_name
        attacking_gang = self.gangs[active_war.attacker_gang]
        defending_gang = self.gangs[active_war.defender_gang]
        
        # Calculate attack power
        attack_power = calculate_attack_power(member.xp, member.territory_contributions)
        
        # Get defenders
        defender_members = [self.members[uid] for uid in defending_gang.members if uid in self.members]
        
        # Calculate defense
        territory_bonus = get_territory_defense_bonus([
            t for t in self.territories.values() 
            if t.controlling_gang == defending_gang.name
        ])
        defense_power = calculate_defense_power(defender_members, territory_bonus)
        
        # Determine outcome
        if is_attacker:
            if attack_power > defense_power:
                # Attacker wins this round
                active_war.attacker_score += 1
                xp_gain = random.randint(*XP_PER_ATTACK_WIN)
                coins_gain = random.randint(*COINS_PER_ATTACK_WIN)
                respect_gain = random.randint(*RESPECT_PER_ATTACK)
                
                # Rare loot chance (10%)
                loot_item, loot_value = get_random_loot() if random.random() < 0.1 else (None, 0)
                
                if active_war.attacker_score >= WAR_WIN_SCORE:
                    return self.end_war(active_war.id, True)
                
                self.update_member_stats(user_id, xp_gain, coins_gain, respect_gain, win=True)
                self.cooldowns[user_id]['war_attack'] = time.time()
                self.save_data()
                
                msg = f"⚔️ You attacked successfully! +{xp_gain}XP, +{coins_gain}💰, +{respect_gain}❤️"
                if loot_item:
                    msg += f"\n🎁 Rare loot: {loot_item} (worth {loot_value}💰)"
                    member.coins += loot_value
                    self.loot_history.append({
                        'user_id': user_id,
                        'item': loot_item,
                        'value': loot_value,
                        'time': datetime.now().isoformat()
                    })
                
                msg += f"\nScore: {active_war.attacker_score}-{active_war.defender_score}"
                return True, msg, None
            else:
                # Defender wins this round
                active_war.defender_score += 1
                xp_gain = random.randint(*XP_PER_ATTACK_LOSS)
                
                if active_war.defender_score >= WAR_WIN_SCORE:
                    return self.end_war(active_war.id, False)
                
                self.update_member_stats(user_id, xp_gain, 0, 0, win=False)
                self.cooldowns[user_id]['war_attack'] = time.time()
                self.save_data()
                return True, f"❌ Your attack was repelled! +{xp_gain}XP\nScore: {active_war.attacker_score}-{active_war.defender_score}", None
        else:
            # Defender attacking back
            if attack_power > defense_power:
                active_war.defender_score += 1
                xp_gain = random.randint(*XP_PER_ATTACK_WIN)
                coins_gain = random.randint(*COINS_PER_ATTACK_WIN)
                respect_gain = random.randint(*RESPECT_PER_ATTACK)
                
                if active_war.defender_score >= WAR_WIN_SCORE:
                    return self.end_war(active_war.id, False)
                
                self.update_member_stats(user_id, xp_gain, coins_gain, respect_gain, win=True)
                self.cooldowns[user_id]['war_attack'] = time.time()
                self.save_data()
                return True, f"⚔️ You counter-attacked! +{xp_gain}XP, +{coins_gain}💰, +{respect_gain}❤️\nScore: {active_war.attacker_score}-{active_war.defender_score}", None
            else:
                active_war.attacker_score += 1
                xp_gain = random.randint(*XP_PER_ATTACK_LOSS)
                
                if active_war.attacker_score >= WAR_WIN_SCORE:
                    return self.end_war(active_war.id, True)
                
                self.update_member_stats(user_id, xp_gain, 0, 0, win=False)
                self.cooldowns[user_id]['war_attack'] = time.time()
                self.save_data()
                return True, f"❌ You were pushed back! +{xp_gain}XP\nScore: {active_war.attacker_score}-{active_war.defender_score}", None
    
    def end_war(self, war_id: str, attacker_won: bool) -> Tuple[bool, str, Optional[Dict]]:
        """End a war and distribute rewards"""
        if war_id not in self.active_wars:
            return False, "❌ War not found!", None
        
        war = self.active_wars[war_id]
        attacking_gang = self.gangs[war.attacker_gang]
        defending_gang = self.gangs[war.defender_gang]
        
        # Determine winner
        if attacker_won:
            winner = attacking_gang
            loser = defending_gang
            winner_name = attacking_gang.name
        else:
            winner = defending_gang
            loser = attacking_gang
            winner_name = defending_gang.name
        
        # Update stats
        winner.wins += 1
        loser.losses += 1
        war.winner = winner_name
        war.status = "completed"
        war.ended_at = datetime.now().isoformat()
        
        # Territory reward (steal a territory)
        loser_territories = [t for t in self.territories.values() if t.controlling_gang == loser.name]
        stolen_territory = None
        if loser_territories:
            stolen_territory = random.choice(loser_territories)
            stolen_territory.controlling_gang = winner.name
            winner.territory += stolen_territory.value
            loser.territory -= stolen_territory.value
        
        # Coins reward
        coins_reward = random.randint(50, 200) * (winner.territory // 2 + 1)
        winner.total_coins += coins_reward
        
        # XP reward
        xp_reward = random.randint(20, 100) * (winner.territory + 1)
        winner.total_xp += xp_reward
        
        # Respect reward
        respect_reward = random.randint(5, 20)
        winner.total_respect += respect_reward
        
        # Ranking points
        ranking_points = random.randint(1, 5)
        winner.total_ranking_points += ranking_points
        
        # Distribute to members
        for uid in winner.members:
            if uid in self.members:
                member = self.members[uid]
                member.xp += xp_reward // 10
                member.coins += coins_reward // 10
                member.respect += respect_reward // 2
                member.wins += 1
                member.territory_contributions += 1
        
        for uid in loser.members:
            if uid in self.members:
                self.members[uid].losses += 1
        
        # Mark war as completed
        del self.active_wars[war_id]
        war.rewards_claimed = True
        
        # Update ranks
        self.update_all_ranks()
        
        self.save_data()
        
        reward_msg = f"🏆 {winner.name} WINS THE WAR! 🏆\n\n"
        reward_msg += f"Rewards:\n"
        if stolen_territory:
            reward_msg += f"• 🏴 Territory captured: {stolen_territory.name}\n"
        else:
            reward_msg += f"• 🏴 No territories captured\n"
        reward_msg += f"• 💰 {coins_reward} coins (gang)\n"
        reward_msg += f"• ⭐ {xp_reward} XP (gang)\n"
        reward_msg += f"• ❤️ {respect_reward} respect (gang)\n"
        reward_msg += f"• 📈 Ranking points: +{ranking_points}"
        
        return True, reward_msg, None
    
    def update_member_stats(self, user_id: int, xp: int, coins: int, respect: int, win: bool):
        """Update member statistics"""
        if user_id not in self.members:
            return
        
        member = self.members[user_id]
        member.xp += xp
        member.coins += coins
        member.respect += respect
        member.attack_count += 1
        
        if win:
            member.wins += 1
        else:
            member.losses += 1
        
        # Update gang totals
        gang = self.gangs[member.gang_name]
        gang.total_xp += xp
        gang.total_coins += coins
        gang.total_respect += respect
        
        # Update rank
        member.rank = get_rank(member.xp)
    
    def update_all_ranks(self):
        """Update ranks for all members"""
        for member in self.members.values():
            member.rank = get_rank(member.xp)
    
    def daily_bonus(self, user_id: int) -> Tuple[bool, str]:
        """Claim daily bonus"""
        if user_id not in self.members:
            return False, "❌ You're not in a gang!"
        
        member = self.members[user_id]
        
        # Check if already claimed today
        if member.last_daily_bonus:
            expired, remaining = is_cooldown_expired(member.last_daily_bonus, DAILY_BONUS_COOLDOWN)
            if not expired:
                return False, f"⏰ Already claimed! Next bonus in {format_time(remaining)}"
        
        # Give bonus
        bonus_coins = random.randint(*DAILY_BONUS_COINS) * (len(self.members) // 10 + 1)
        bonus_xp = random.randint(*DAILY_BONUS_XP)
        bonus_respect = random.randint(*DAILY_BONUS_RESPECT)
        
        # Rare loot chance (5%)
        loot_item, loot_value = get_random_loot() if random.random() < 0.05 else (None, 0)
        
        member.coins += bonus_coins
        member.xp += bonus_xp
        member.respect += bonus_respect
        
        if loot_item:
            member.coins += loot_value
            self.loot_history.append({
                'user_id': user_id,
                'item': loot_item,
                'value': loot_value,
                'time': datetime.now().isoformat()
            })
        
        member.last_daily_bonus = datetime.now().isoformat()
        member.rank = get_rank(member.xp)
        self.save_data()
        
        msg = f"✅ Daily bonus claimed!\n💰 +{bonus_coins} coins\n⭐ +{bonus_xp} XP\n❤️ +{bonus_respect} respect"
        if loot_item:
            msg += f"\n🎁 Rare loot: {loot_item} (worth {loot_value}💰)"
        
        return True, msg
    
    def get_gang_info(self, gang_name: str) -> str:
        """Get formatted gang information"""
        if gang_name not in self.gangs:
            return "❌ Gang not found!"
        
        gang = self.gangs[gang_name]
        members_list = []
        for uid in gang.members[:15]:
            if uid in self.members:
                member = self.members[uid]
                leader_tag = " 👑" if uid == gang.leader_id else ""
                members_list.append(f"• {member.username} ({member.rank}){leader_tag}")
        
        if len(gang.members) > 15:
            members_list.append(f"... and {len(gang.members) - 15} more")
        
        info = f"{gang.color} {gang.name}\n"
        info += f"👑 Leader: {self.members.get(gang.leader_id, {}).username if gang.leader_id in self.members else 'Unknown'}\n"
        info += f"👥 Members: {len(gang.members)}/{MAX_MEMBERS_PER_GANG}\n"
        info += f"🏴 Territories: {gang.territory}\n"
        info += f"⭐ Total XP: {gang.total_xp}\n"
        info += f"💰 Total Coins: {gang.total_coins}\n"
        info += f"❤️ Respect: {gang.total_respect}\n"
        info += f"⚔️ W/L: {gang.wins}/{gang.losses}\n"
        info += f"📈 Ranking Points: {gang.total_ranking_points}\n\n"
        info += "👥 Members:\n" + "\n".join(members_list)
        
        return info
    
    def get_leaderboard(self) -> str:
        """Get gang leaderboard"""
        sorted_gangs = sorted(
            self.gangs.values(), 
            key=lambda g: g.total_ranking_points + g.total_xp // 100, 
            reverse=True
        )
        
        board = "🏆 GANG LEADERBOARD 🏆\n\n"
        for i, gang in enumerate(sorted_gangs[:10], 1):
            score = gang.total_ranking_points + gang.total_xp // 100
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}.")
            board += f"{medal} {gang.color} {gang.name}: {score} pts\n"
            board += f"   📊 {gang.wins}W {gang.losses}L | 🏴 {gang.territory}\n"
        
        return board
    
    def get_member_stats(self, user_id: int) -> str:
        """Get member statistics"""
        if user_id not in self.members:
            return "❌ You're not in a gang!"
        
        member = self.members[user_id]
        gang = self.gangs[member.gang_name]
        
        stats = f"📊 {member.username}'s Stats\n"
        stats += f"🏴 Gang: {gang.color} {member.gang_name}\n"
        stats += f"👑 Rank: {member.rank}\n"
        stats += f"⭐ XP: {member.xp}\n"
        stats += f"💰 Coins: {member.coins}\n"
        stats += f"❤️ Respect: {member.respect}\n"
        stats += f"⚔️ W/L: {member.wins}/{member.losses}\n"
        stats += f"🏴 Territory contributions: {member.territory_contributions}\n"
        stats += f"🎯 Attacks: {member.attack_count}\n"
        stats += f"📅 Joined: {member.joined_at[:10]}"
        
        return stats
    
    def get_war_status(self, user_id: int) -> str:
        """Get active war status"""
        if user_id not in self.members:
            return "❌ You're not in a gang!"
        
        member = self.members[user_id]
        gang_name = member.gang_name
        
        active_war = None
        for war in self.active_wars.values():
            if war.attacker_gang == gang_name or war.defender_gang == gang_name:
                active_war = war
                break
        
        if not active_war:
            return "ℹ️ Your gang is not in an active war."
        
        attacker_gang = self.gangs[active_war.attacker_gang]
        defender_gang = self.gangs[active_war.defender_gang]
        
        status = f"⚔️ ACTIVE WAR ⚔️\n\n"
        status += f"{attacker_gang.color} {active_war.attacker_gang}\n"
        status += f"VS\n"
        status += f"{defender_gang.color} {active_war.defender_gang}\n\n"
        status += f"Score: {active_war.attacker_score} - {active_war.defender_score}\n"
        status += f"First to {WAR_WIN_SCORE} wins!\n"
        status += f"👥 Participants: {len(active_war.participants)}\n"
        
        # Show top participants
        if active_war.participants:
            status += "\nTop fighters:\n"
            for uid in active_war.participants[:5]:
                if uid in self.members:
                    status += f"• {self.members[uid].username}\n"
        
        return status
    
    def get_territories_info(self) -> str:
        """Get territory information"""
        msg = "🏴 TERRITORY CONTROL 🏴\n\n"
        
        for territory in sorted(self.territories.values(), key=lambda t: t.value, reverse=True):
            controller = territory.controlling_gang or "Unowned"
            color = self.gangs[controller].color if controller in self.gangs else "⚪"
            msg += f"{color} {territory.name}\n"
            msg += f"   👑 {controller}\n"
            msg += f"   💰 Value: {territory.value} | 🛡️ Defense: +{territory.defense_bonus}\n"
            msg += "\n"
        
        return msg
    
    def get_top_players(self) -> str:
        """Get top players leaderboard"""
        sorted_players = sorted(
            self.members.values(),
            key=lambda m: m.xp + m.respect * 5,
            reverse=True
        )
        
        board = "👑 TOP PLAYERS 👑\n\n"
        for i, player in enumerate(sorted_players[:10], 1):
            score = player.xp + player.respect * 5
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}.")
            gang = self.gangs.get(player.gang_name)
            color = gang.color if gang else "⚪"
            board += f"{medal} {color} {player.username} - {player.rank}\n"
            board += f"   ⭐ Score: {score} | ⚔️ {player.wins}W\n"
        
        return board
