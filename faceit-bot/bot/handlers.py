from telegram import Update
from telegram.ext import ContextTypes
from faceit_api.playermatches import get_players_matches
from faceit_api.playerprofile import find_player_profile, get_player_stats
from keyboards import get_menu_keyboard

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to the Faceit Bot! Choose an option below.",
        reply_markup=get_menu_keyboard()
    )

async def player_info(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("Please enter the player's nickname:")
    context.user_data['state'] = 'PLAYER_INFO'

async def matches_info(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Please enter the player's ID and the number of hours (default is 24).\n"
        "Format: player_id hours\n"
        "Example: abc123 12"
    )
    context.user_data['state'] = 'PLAYERS_MATCHES'

async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_input = update.message.text

    if context.user_data.get('state') == 'PLAYER_INFO':
        nickname = user_input
        profile = find_player_profile(nickname)

        if profile:
            player_id = profile['player_id']
            stats = get_player_stats(player_id)

            if stats:
                response = (
                    f"Nickname: {profile['nickname']}\n"
                    f"Faceit player ID: {player_id}\n"
                    f"ELO: {profile['elo']}\n"
                    f"Games connected: {', '.join(profile['games'].keys())}\n\n"
                    f"Last {stats['matches_count']} Matches Statistics:\n"
                    f"Average Kills: {stats['average_kills']}\n"
                    f"Average Headshots %: {stats['average_headshots_percentage']}%\n"
                    f"Average K/D: {stats['average_kd']}\n"
                    f"Average K/R: {stats['average_kr']}"
                )
            else:
                response = (
                    f"Nickname: {profile['nickname']}\n"
                    f"Faceit player ID: {player_id}\n"
                    f"ELO: {profile['elo']}\n"
                    f"Games connected: {', '.join(profile['games'].keys())}\n\n"
                    "No match statistics available."
                )
        else:
            response = "Player not found."

        await update.message.reply_text(response, reply_markup=get_menu_keyboard())
        context.user_data['state'] = None

    elif context.user_data.get('state') == 'PLAYERS_MATCHES':
        try:
            parts = user_input.split()
            if len(parts) == 1:
                nickname = parts[0]
                profile = find_player_profile(nickname)
                if profile:
                    player_id = profile['player_id']
                    hours = 24  
                else:
                    await update.message.reply_text("Player not found.")
                    return
            elif len(parts) == 2:
                player_id = parts[0]
                hours = int(parts[1])
            else:
                await update.message.reply_text(
                    "Invalid format. Please use the format: <player_id> <hours> or <nickname>."
                )
                return

            matches_count = get_players_matches(player_id, hours=hours)
            response = f"Player has played {matches_count} matches in the last {hours} hours."
        except Exception as e:
            response = f"Error fetching matches: {e}"

        await update.message.reply_text(response, reply_markup=get_menu_keyboard())
        context.user_data['state'] = None
