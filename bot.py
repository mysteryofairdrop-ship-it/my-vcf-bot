import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Bot Token (Render par environment variable set karenge)
BOT_TOKEN = os.environ.get('8040780554:AAGeKP-K5-_jD0HNpNwOhv770u_tdFbBovs')
# Apna Telegram User ID (7025016111)
ADMIN_USER_ID = int(os.environ.get('ADMIN_USER_ID', 'YOUR_USER_ID_HERE'))

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Store authorized users
AUTHORIZED_USERS = set()
PENDING_REQUESTS = {}  # {user_id: user_info}

# /start command - Permission mangne ke liye
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    username = update.message.from_user.username
    
    if user_id in AUTHORIZED_USERS:
        await update.message.reply_text(
            "Namaste! 👋 Main VCF Bot hoon.\n"
            "Mujhe kisi ka naam, phone number, email, aur anya details bhejiye, main aapko VCF file bana kar dunga.\n\n"
            "Example:\n"
            "Name: Raj Sharma\n"
            "Phone: +919876543210\n"
            "Email: raj@example.com"
        )
        return
    
    # Admin ko request bhejein
    PENDING_REQUESTS[user_id] = {
        'name': user_name,
        'username': username
    }
    
    request_msg = (
        "🔔 Naya Access Request:\n"
        f"User: {user_name}\n"
        f"Username: @{username if username else 'N/A'}\n"
        f"User ID: {user_id}\n\n"
        f"Approve: /approve_{user_id}\n"
        f"Reject: /reject_{user_id}"
    )
    
    try:
        await context.bot.send_message(chat_id=ADMIN_USER_ID, text=request_msg)
        await update.message.reply_text(
            "✅ Access request bhej di gayi hai admin ko!\n"
            "Jab admin approve karenge tab aap bot use kar payenge.\n"
            "Kripya thoda intezar karein..."
        )
    except:
        await update.message.reply_text("❌ Admin tak request nahi pahuch payi. Baad mein try karein.")

# Admin commands - Approve/Reject karne ke liye
async def approve_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_USER_ID:
        await update.message.reply_text("❌ Sirf admin hi yeh command use kar sakte hain.")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /approve USER_ID")
        return
    
    try:
        user_id = int(context.args[0])
        if user_id in PENDING_REQUESTS:
            AUTHORIZED_USERS.add(user_id)
            user_info = PENDING_REQUESTS[user_id]
            del PENDING_REQUESTS[user_id]
            
            # User ko notification bhejein
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text="🎉 Aapko access approve kar diya gaya hai! Ab aap /start command use kar sakte hain."
                )
            except:
                pass
            
            await update.message.reply_text(f"✅ User {user_info['name']} (@{user_info['username']}) ko access approve kar diya gaya hai.")
        else:
            await update.message.reply_text("❌ Yeh user ID pending requests mein nahi hai.")
    except ValueError:
        await update.message.reply_text("❌ Sahi user ID daalein.")

async def reject_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_USER_ID:
        await update.message.reply_text("❌ Sirf admin hi yeh command use kar sakte hain.")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /reject USER_ID")
        return
    
    try:
        user_id = int(context.args[0])
        if user_id in PENDING_REQUESTS:
            user_info = PENDING_REQUESTS[user_id]
            del PENDING_REQUESTS[user_id]
            
            # User ko notification bhejein (optional)
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text="❌ Aapki access request reject kar di gayi hai."
                )
            except:
                pass
            
            await update.message.reply_text(f"❌ User {user_info['name']} (@{user_info['username']}) ki request reject kar di gayi hai.")
        else:
            await update.message.reply_text("❌ Yeh user ID pending requests mein nahi hai.")
    except ValueError:
        await update.message.reply_text("❌ Sahi user ID daalein.")

# List pending requests
async def pending_requests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_USER_ID:
        await update.message.reply_text("❌ Sirf admin hi yeh command use kar sakte hain.")
        return
    
    if not PENDING_REQUESTS:
        await update.message.reply_text("✅ Koi pending requests nahi hain.")
        return
    
    message = "📋 Pending Access Requests:\n\n"
    for user_id, user_info in PENDING_REQUESTS.items():
        message += f"User: {user_info['name']} (@{user_info['username']})\n"
        message += f"ID: {user_id}\n"
        message += f"Approve: /approve_{user_id}\n"
        message += f"Reject: /reject_{user_id}\n\n"
    
    await update.message.reply_text(message)

# VCF generate karne wala function (same as before)
def generate_vcf(name, phone, email=None, org=None):
    vcf_content = f"""BEGIN:VCARD
VERSION:3.0
FN:{name}
TEL;TYPE=CELL:{phone}
"""
    if email:
        vcf_content += f"EMAIL:{email}\n"
    if org:
        vcf_content += f"ORG:{org}\n"
    vcf_content += "END:VCARD"
    return vcf_content

# Message handle karein (sirf authorized users ke liye)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("❌ Aapke paas access nahi hai. Pehle /start karein aur wait karein.")
        return
    
    user_text = update.message.text
    lines = user_text.split('\n')
    data = {}
    
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            data[key.strip().lower()] = value.strip()
    
    name = data.get('name', 'Unknown')
    phone = data.get('phone', '')
    email = data.get('email', '')
    org = data.get('org', '')
    
    if not phone:
        await update.message.reply_text("Phone number diye bina VCF nahi bana sakta. Kripya phone number provide karein.")
        return
    
    vcf_data = generate_vcf(name, phone, email, org)
    
    # VCF file save karein temporarily
    filename = f"{name.replace(' ', '_')}.vcf"
    with open(filename, 'w') as f:
        f.write(vcf_data)
    
    # File send karein
    with open(filename, 'rb') as f:
        await update.message.reply_document(document=f, caption="Yeh lo aapki VCF file! 📇")
    
    # Temporary file delete karein
    os.remove(filename)

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("approve", approve_user))
    application.add_handler(CommandHandler("reject", reject_user))
    application.add_handler(CommandHandler("pending", pending_requests))
    
    # Message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling()

if __name__ == '__main__':
    main()