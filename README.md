# gang-wars-bot
# 🏙️ Gang Wars Telegram Bot

A multiplayer gang warfare game bot for Telegram where players can create gangs, battle for territory, and earn rewards.

## Features

- **Create & Manage Gangs** - Create gangs with custom names and colors
- **Multiplayer Wars** - Declare war on other gangs with 5-point victory system
- **Territory Control** - Capture territories for bonuses and rewards
- **Rank System** - Progress from Recruit to Legend based on XP
- **Daily Bonuses** - Claim daily rewards including rare loot
- **Leaderboards** - Compete for top gang and player rankings
- **Anti-Farming** - Cooldowns prevent abuse

## Rewards

- 🏴 Territory control
- 💰 Coins
- ⭐ XP
- ❤️ Respect
- 🎁 Rare loot drops
- 📈 Ranking points

## Commands

### Gang Management
- `/creategang <name> <color>` - Create a new gang
- `/joingang <name>` - Join an existing gang
- `/leavegang` - Leave your current gang
- `/transfer @username` - Transfer leadership
- `/ganginfo` - View your gang's info
- `/myprofile` - View your stats

### War System
- `/startwar <gang>` - Declare war on another gang
- `/warattack` - Attack in active war
- `/warstatus` - Check active war status

### Rewards & Info
- `/daily` - Claim daily bonus
- `/leaderboard` - View gang rankings
- `/territories` - View territory control
- `/top` - View top players
- `/help` - Show help menu

## Deployment to Heroku

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/gang-wars-bot.git
cd gang-wars-bot
