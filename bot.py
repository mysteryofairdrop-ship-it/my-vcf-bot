# bot.py mein yeh code add karein
AUTHORIZED_USERS = {}  # Store authorized users
BOT_PASSWORD = "MY_SECRET_PASSWORD"  # Change this to your password

async def authenticate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if len(context.args) == 0:
        await update.message.reply_text("Please enter password: /auth YOUR_PASSWORD")
        return
    
    password_attempt = context.args[0]
    if password_attempt == BOT_PASSWORD:
        AUTHORIZED_USERS[user_id] = True
        await update.message.reply_text("✅ Authentication successful! You can now use the bot.")
    else:
        await update.message.reply_text("❌ Invalid password. Access denied.")

# Har command se pehle check karein
def is_authorized(user_id):
    return user_id in AUTHORIZED_USERS

# Start command modify karein
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not is_authorized(user_id):
        await update.message.reply_text(
            "🔒 This is a private bot. Please authenticate using: /auth YOUR_PASSWORD"
        )
        return
        
    await update.message.reply_text("Namaste! 👋 Main VCF Bot hoon...")