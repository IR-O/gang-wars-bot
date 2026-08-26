import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    CallbackQueryHandler, 
    ContextTypes, 
    MessageHandler, 
    filters
)

from config import BOT_TOKEN, PORT
from game import GangWarsGame

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize game
game = GangWarsGame()

# ==================== Helper Functions ====================
def get_main_keyboard():
    """Get main keyboard markup"""
    keyboard = [
        [
            InlineKeyboardButton("🏴 Gang", callback_data="gang_menu"),
            InlineKeyboardButton("⚔️ War", callback_data="war_menu")
        ],
        [
            InlineKeyboardButton("💰 Daily", callback_data="daily"),
            InlineKeyboardButton("🏆 Top", callback_data="top")
        ],
        [
            InlineKeyboardButton("📊 Leaderboard", callback_data="leaderboard"),
            InlineKeyboardButton("🏴 Territories", callback_data="territories")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# ==================== Command Handlers ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    user = update.effective_user
    welcome = (
        f"🏙️ Welcome to GANG WARS, {user.first_name}!\n\n"
        "🔥 Build your gang, conquer territories, and dominate the city!\n\n"
        "📋 Commands:\n"
        "/creategang <name> <color> - Start your own gang\n"
        "/joingang <name> - Join an existing gang\n"
        "/leavegang - Leave your current gang\n"
        "/ganginfo - View your gang's info\n"
        "/myprofile - View your stats\n"
        "/startwar <gang> - Declare war on another gang\n"
        "/warattack - Attack in the current war\n"
        "/warstatus - Check active war status\n"
        "/daily - Claim your daily bonus\n"
        "/leaderboard - View gang rankings\n"
        "/territories - View territory control\n"
        "/top - View top players\n"
        "/help - Show this menu\n\n"
        "🎨 Colors: 🔴RED 🔵BLUE 🟢GREEN 🟡YELLOW 🟣PURPLE 🟠ORANGE"
    )
    await update.message.reply_text(welcome, reply_markup=get_main_keyboard())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    help_text = (
        "📖 GANG WARS HELP\n\n"
        "🏗️ Gang Management:\n"
        "/creategang <name> <color> - Create a gang\n"
        "/joingang <name> - Join a gang\n"
        "/leavegang - Leave your gang\n"
        "/transfer <@username> - Transfer leadership\n"
        "/ganginfo - View gang info\n"
        "/myprofile - View your stats\n\n"
        "⚔️ War Commands:\n"
        "/startwar <gang> - Declare war\n"
        "/warattack - Attack in active war\n"
        "/warstatus - Check war status\n\n"
        "💰 Rewards:\n"
        "/daily - Claim daily bonus\n"
        "/leaderboard - View rankings\n"
        "/territories - View territory control\n"
        "/top - View top players\n\n"
        "🏆 Rewards include:\n"
        "• Territory control 🏴\n"
        "• Coins 💰\n"
        "• XP ⭐\n"
        "• Respect ❤️\n"
        "• Rare loot drops 🎁\n"
        "• Ranking points 📈"
    )
    await update.message.reply_text(help_text, reply_markup=get_main_keyboard())

async def create_gang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create a new gang"""
    user = update.effective_user
    args = context.args
    
    if len(args) < 2:
        await update.message.reply_text(
            "Usage: /creategang <name> <color>\n"
            "Colors: 🔴RED 🔵BLUE 🟢GREEN 🟡YELLOW 🟣PURPLE 🟠ORANGE"
        )
        return
    
    gang_name = args[0]
    color = args[1]
    
    if color not in ["🔴", "🔵", "🟢", "🟡", "🟣", "🟠"]:
        await update.message.reply_text(
            "❌ Invalid color! Use: 🔴RED 🔵BLUE 🟢GREEN 🟡YELLOW 🟣PURPLE 🟠ORANGE"
        )
        return
    
    success, msg = game.create_gang(user.id, user.username or user.first_name, gang_name, color)
    await update.message.reply_text(msg, reply_markup=get_main_keyboard())

async def join_gang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Join an existing gang"""
    user = update.effective_user
    args = context.args
    
    if not args:
        await update.message.reply_text("Usage: /joingang <gang_name>")
        return
    
    gang_name = args[0]
    success, msg = game.join_gang(user.id, user.username or user.first_name, gang_name)
    await update.message.reply_text(msg, reply_markup=get_main_keyboard())

async def leave_gang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Leave current gang"""
    user = update.effective_user
    success, msg = game.leave_gang(user.id)
    await update.message.reply_text(msg, reply_markup=get_main_keyboard())

async def transfer_leadership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Transfer gang leadership"""
    user = update.effective_user
    args = context.args
    
    if not args:
        await update.message.reply_text("Usage: /transfer @username")
        return
    
    new_leader = args[0].replace('@', '')
    success, msg = game.transfer_leadership(user.id, new_leader)
    await update.message.reply_text(msg, reply_markup=get_main_keyboard())

async def gang_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View gang information"""
    user = update.effective_user
    args = context.args
    
    if args:
        gang_name = args[0]
        info = game.get_gang_info(gang_name)
        await update.message.reply_text(info, reply_markup=get_main_keyboard())
        return
    
    if user.id not in game.members:
        await update.message.reply_text(
            "❌ You're not in a gang! Use /creategang or /joingang",
            reply_markup=get_main_keyboard()
        )
        return
    
    member = game.members[user.id]
    info = game.get_gang_info(member.gang_name)
    await update.message.reply_text(info, reply_markup=get_main_keyboard())

async def my_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View member profile"""
    user = update.effective_user
    stats = game.get_member_stats(user.id)
    await update.message.reply_text(stats, reply_markup=get_main_keyboard())

async def start_war(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start a war"""
    user = update.effective_user
    args = context.args
    
    if not args:
        await update.message.reply_text("Usage: /startwar <gang_name>")
        return
    
    defender = args[0]
    success, msg = game.start_war(user.id, defender)
    await update.message.reply_text(msg, reply_markup=get_main_keyboard())

async def war_attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Attack in current war"""
    user = update.effective_user
    
    if user.id not in game.members:
        await update.message.reply_text("❌ You're not in a gang!")
        return
    
    success, msg, _ = game.war_attack(user.id)
    await update.message.reply_text(msg, reply_markup=get_main_keyboard())

async def war_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check war status"""
    user = update.effective_user
    status = game.get_war_status(user.id)
    await update.message.reply_text(status, reply_markup=get_main_keyboard())

async def daily_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Claim daily bonus"""
    user = update.effective_user
    success, msg = game.daily_bonus(user.id)
    await update.message.reply_text(msg, reply_markup=get_main_keyboard())

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show leaderboard"""
    board = game.get_leaderboard()
    await update.message.reply_text(board, reply_markup=get_main_keyboard())

async def territories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show territory control"""
    info = game.get_territories_info()
    await update.message.reply_text(info, reply_markup=get_main_keyboard())

async def top_players(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show top players"""
    board = game.get_top_players()
    await update.message.reply_text(board, reply_markup=get_main_keyboard())

# ==================== Callback Query Handlers ====================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    data = query.data
    
    if data == "gang_menu":
        if user.id in game.members:
            member = game.members[user.id]
            info = game.get_gang_info(member.gang_name)
            await query.edit_message_text(info, reply_markup=get_main_keyboard())
        else:
            await query.edit_message_text(
                "❌ You're not in a gang!\nUse /creategang or /joingang",
                reply_markup=get_main_keyboard()
            )
    
    elif data == "war_menu":
        status = game.get_war_status(user.id)
        await query.edit_message_text(status, reply_markup=get_main_keyboard())
    
    elif data == "daily":
        success, msg = game.daily_bonus(user.id)
        await query.edit_message_text(msg, reply_markup=get_main_keyboard())
    
    elif data == "leaderboard":
        board = game.get_leaderboard()
        await query.edit_message_text(board, reply_markup=get_main_keyboard())
    
    elif data == "territories":
        info = game.get_territories_info()
        await query.edit_message_text(info, reply_markup=get_main_keyboard())
    
    elif data == "top":
        board = game.get_top_players()
        await query.edit_message_text(board, reply_markup=get_main_keyboard())

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"Update {update} caused error {context.error}")

# ==================== Main Application ====================
def main():
    """Start the bot"""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("creategang", create_gang))
    application.add_handler(CommandHandler("joingang", join_gang))
    application.add_handler(CommandHandler("leavegang", leave_gang))
    application.add_handler(CommandHandler("transfer", transfer_leadership))
    application.add_handler(CommandHandler("ganginfo", gang_info))
    application.add_handler(CommandHandler("myprofile", my_profile))
    application.add_handler(CommandHandler("startwar", start_war))
    application.add_handler(CommandHandler("warattack", war_attack))
    application.add_handler(CommandHandler("warstatus", war_status))
    application.add_handler(CommandHandler("daily", daily_bonus))
    application.add_handler(CommandHandler("leaderboard", leaderboard))
    application.add_handler(CommandHandler("territories", territories))
    application.add_handler(CommandHandler("top", top_players))
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("Starting Gang Wars bot...")
    
    # For Heroku deployment
    if os.environ.get('DYNO'):
        application.run_webhook(
            listen='0.0.0.0',
            port=PORT,
            url_path=BOT_TOKEN,
            webhook_url=f"https://{os.environ.get('HEROKU_APP_NAME')}.herokuapp.com/{BOT_TOKEN}"
        )
    else:
        # Local development
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
