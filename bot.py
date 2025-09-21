import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from Crypto.Cipher import DES
import base64
import sqlite3

# ==================== CONFIGURATION ====================
BOT_TOKEN = os.environ.get('8345588914:AAGsPHUAU2vU-_UqkvlUpttGfIrPS_kws6g')  # Render par set karenge
ADMIN_ID = int(os.environ.get('7025016111'))  # Aapka User ID
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', 'Farhan12')  # Aapki secret key

# ==================== ENCRYPTION ====================
def generate_activation_key(user_id):
    cipher = DES.new(ENCRYPTION_KEY.encode(), DES.MODE_ECB)
    padded_id = str(user_id).ljust(8)
    encrypted = cipher.encrypt(padded_id.encode())
    return base64.b64encode(encrypted).decode()

def verify_activation_key(key, user_id):
    try:
        cipher = DES.new(ENCRYPTION_KEY.encode(), DES.MODE_ECB)
        decoded = base64.b64decode(key)
        decrypted = cipher.decrypt(decoded).decode().strip()
        return decrypted == str(user_id)
    except:
        return False

# ==================== DATABASE ====================
def init_db():
    conn = sqlite3.connect('bot_users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            activated INTEGER DEFAULT 0,
            activation_key TEXT
        )
    ''')
    conn.commit()
    conn.close()

# ==================== COMMANDS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    init_db()
    
    conn = sqlite3.connect('bot_users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT activated FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    
    if user and user[0] == 1:
        await update.message.reply_text('✅ Bot activated! Welcome! Use /vcf to create a VCF card.')
    else:
        activation_key = generate_activation_key(user_id)
        cursor.execute('INSERT OR REPLACE INTO users (user_id, activated, activation_key) VALUES (?, ?, ?)',
                      (user_id, 0, activation_key))
        conn.commit()
        await update.message.reply_text(
            f'🔒 Bot not activated. Please send this ID to admin: `{user_id}`\n'
            f'Then use /activate YOUR_KEY to activate'
        )
    conn.close()

async def activate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text('❌ Please provide activation key: /activate YOUR_KEY')
        return
        
    user_id = update.effective_user.id
    user_key = context.args[0]
    
    conn = sqlite3.connect('bot_users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT activation_key FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    
    if user and verify_activation_key(user_key, user_id):
        cursor.execute('UPDATE users SET activated = 1 WHERE user_id = ?', (user_id,))
        conn.commit()
        await update.message.reply_text('✅ Bot activated successfully! Now use /vcf')
    else:
        await update.message.reply_text('❌ Invalid activation key. Contact admin.')
    conn.close()

async def vcf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conn = sqlite3.connect('bot_users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT activated FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user and user[0] == 1:
        # Yahan aap VCF banane ka code add kar sakte hain
        vcf_data = "BEGIN:VCARD\nVERSION:3.0\nFN:Farhan\nTEL:+911234567890\nEND:VCARD"
        await update.message.reply_text("✅ Here is your VCF card:")
        await update.message.reply_document(document=open('example.vcf', 'wb'), filename='contact.vcf')
    else:
        await update.message.reply_text("❌ Bot not activated. Use /start first.")

# ==================== MAIN ====================
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("activate", activate))
    application.add_handler(CommandHandler("vcf", vcf))
    
    print("Bot started...")
    application.run_polling()

if __name__ == "__main__":
    main()