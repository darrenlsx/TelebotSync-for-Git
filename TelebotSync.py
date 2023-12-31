from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from database_handler import Firebase
from util import Event

import token_name

## Set up Telegram Bot
import telebot
from telebot import types

# Add private token key
TOKEN = token_name.token

bot = telebot.TeleBot(TOKEN, parse_mode=None)

## Set up Google API
SCOPES = ['https://www.googleapis.com/auth/calendar']
creds = None
song_name = ""

# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

service = build('calendar', 'v3', credentials=creds)

# List of Commands
@bot.message_handler(commands=['add'])
def create_event(message):
    reply = bot.send_message(message.chat.id, "What is the song title to add? Note no symbols pls only letters and whitespaces")
    def get_song_name(message):
        global song_name
        song_name = message.text
        print(song_name)
        bot.send_message(message.chat.id, "Okai adding for song title: {}\n\nPlease type in the dates in the proper format\nDate: DD/MM/YY _(day)_\nTime: HH.MMam/pm - HH.MMam/pm\nCMI:\nAgenda:\n\nYou may leave CMI or Agenda empty.\nThe (day) is optional, doesnt affect the bot, just for your ez ref if want to paste in grpchat.\nIf you need an example enter /eg and go back to /add again to continue.\nYou can copy the below message to get started.".format(song_name), parse_mode="Markdown")
        bot.send_message(message.chat.id, "Date:\nTime:\nCMI:\nAgenda:\n ")
    bot.register_next_step_handler(reply, get_song_name)

@bot.message_handler(commands=['start'])
def welcome_message(message):
    bot.send_message(message.chat.id, "Hello, welcome to N.Trance Sync, enter /menu to begin :>\nDo note we have an update with the adding of events so now MUST include the year.\nCheck out /eg for an example.")


@bot.message_handler(commands=['menu'])
def handle_m(message):

    keyboard = types.InlineKeyboardMarkup()
    b1 = types.InlineKeyboardButton('/add: Add Date(s)', callback_data='add')
    b2 = types.InlineKeyboardButton('/eg: Example Format', callback_data='eg')
    b3 = types.InlineKeyboardButton('/delete: Delete Date', callback_data='delete')
    keyboard.row(b1)
    keyboard.row(b2)
    keyboard.row(b3)
    commands = "Here are the commands :)\n/start   : Welcome message\n\n/add     : Prompts user for song title and dates to add to calendar\n\n/eg       : Provides an example in proper format/delete : Prompts user to choose which song title to delete from and will be given a list of song dates currently registered in calendar\n\n/delete : Prompts user to choose which song title to delete from and will be given a list of song dates currently registered in calendar\n"

    bot.send_message(message.chat.id, commands,reply_markup=keyboard)

@bot.callback_query_handler(func=lambda c:True)
def handle_menu_click(c):
    if (c.data == "add"):
        create_event(c.message)
    elif (c.data == "eg"):
        example_message(c.message)
    elif (c.data == "delete"):
        delete_event(c.message)

# @bot.message_handler(commands=['help'])
# def help_message(message):
#     bot.send_message(message.chat.id, "/start   : Welcome message\n/add     : Prompts user for song title and dates to add to calendar\n/delete : Prompts user to choose which song title to delete from and will be given a list of song dates currently registered in calendar\n/eg       : Provides an example in proper format")

@bot.message_handler(commands=['eg'])
def example_message(message):
    bot.send_message(message.chat.id, "Date: 01/02/23\nTime: 9.00am - 10.30pm\nCMI: IU :/ she'll come after 8pm (hopefully)\nAgenda: Clean till chorus\n\nDate: 02/02/23\nTime: 10.00am - 12.00pm\nCMI: Full crew\nAgenda: Filming at MBS")
                     
@bot.message_handler(commands=['delete'])
def delete_event(message):
    reply = bot.send_message(message.chat.id, "Which song title you want to delete from?")        
    bot.register_next_step_handler(reply, handle_delete_event)

def handle_delete_event(message):
    global service
    try:
        # Call the Calendar API
        events_result = service.events().list(calendarId='primary',
                                            maxResults=None, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        message_list = ""
        filtered_id_list  = []
        counter = 1
        for i in range(len(events)):
            if (events[i]['summary'].lower().replace(" ", "") == message.text.lower().replace(" ","")):
                message_list += str(counter) + ") " + rfc3339_to_GMT_converter(events[i]['start'].get('dateTime', events[i]['start'].get('date')), events[i]['end'].get('dateTime', events[i]['end'].get('date')))+ "\n"
                filtered_id_list.append(events[i]['id'])
                counter += 1
        
        if (len(filtered_id_list) == 0):
            bot.send_message(message.chat.id, "Sorry song title not found :( Pls type /delete again")
            return

        bot.send_message(message.chat.id, message_list)
        reply_index = bot.send_message(message.chat.id, "Which number do you want to delete? To delete multiple dates use comma to separate, for eg: [number],[number],...")

        # Deletes the event
        def delete_event_handler(message):
            try:
                events_to_delete = delete_command_string_handler(message.text)
                
                for i in range(0, len(events_to_delete)):
                    if (int(events_to_delete[i]) <= 0 or int(events_to_delete[i]) > len(filtered_id_list)):
                        bot.send_message(message.chat.id, "Sorry number: {} not found :(".format(events_to_delete[i]))
                        print(len(events_to_delete))
                        print(events_to_delete[i])
                    else:
                        service.events().delete(calendarId='primary', eventId=filtered_id_list[int(events_to_delete[i])-1]).execute()
                        bot.send_message(message.chat.id, "Okai deleted number: {}".format(events_to_delete[i]))
                        
                bot.send_message(message.chat.id, "Enter /delete again if you wish to continue deleting")
            except ValueError:
                bot.send_message(message.chat.id, "Sorry that's not a number. Enter /delete again if you wish to continue deleting")

        bot.register_next_step_handler(reply_index, delete_event_handler)

    except HttpError as error:
        print('An error occurred: %s' % error)

# Handles the given input of string to delete from calendar
def delete_command_string_handler(message):
    events_to_delete = []
    spliced_numbers = message.split(",")
    for i in range(0, len(spliced_numbers)):
        events_to_delete.append(spliced_numbers[i].strip())
    return events_to_delete

def rfc3339_to_GMT_converter(start, end):
    date = start[8:10]+ "/" + start[5:7] + "/" + start[2:4]
    return date + " at " + time_check(start) + " - " + time_check(end)

def time_check(s):
    time24hr_hr = int(s.split("T")[1].split(":")[0])
    time_min = s.split("T")[1].split(":")[1]
    if (time24hr_hr >= 12):
        time24hr_hr -= 12
        return str(time24hr_hr) + "." + time_min + "pm"
    return str(time24hr_hr) + "." + time_min + "am" 
    
# Prepares given input events from user
@bot.message_handler(func=lambda message: True)
def event_handler(message):
  if ("Date" in message.text):
    handle_message(message.text, message)    
  else:
      bot.send_message(message.chat.id, "Sorry me no understand :( Please type in correct command")
    
# Handles given input events from user
def handle_message(text, message):
    lines = text.splitlines()
    event_list = []
    dict = {}
    print(lines)
    for i in range(len(lines)):
        if (len(lines[i]) > 1):
            arr = lines[i].split(":")
            dict[arr[0].rstrip()] = arr[1].strip()

        # Next event/Exit
        if (len(lines[i]) <= 1 or i == len(lines) - 1):
            event_list.append(Event(dict["Date"], dict["Time"], dict["CMI"], dict["Agenda"]))
            # print(dict)
            dict = {}

    global service
    try:
        for e in event_list:
            
            global song_name

            time_converted = date_converter(e.date, e.time)
            event = {
                'summary': '{}'.format(song_name) ,
                'description': 'CMI: {}\nAgenda: {}'.format(e.cmi, e.agenda),
                'start': {
                    'dateTime': '{}'.format(time_converted[0]),
                    'timeZone': 'Asia/Singapore',
                },
                'end': {
                    'dateTime': '{}'.format(time_converted[1]),
                    'timeZone': 'Asia/Singapore',
                },
            }
            service.events().insert(calendarId='primary', body=event).execute()
            bot.send_message(message.chat.id, "Okay added into calendar")
            print(event)
    except (HttpError, IndexError):
        bot.send_message(message.chat.id, "Sorry incorrect format. Please check again and start from /add")

# Converts date-time to rf3339 format
def date_converter(date, time):
    spliced_day = date[:2]
    spliced_month = date[3:5]
    spliced_year = date[6:10]

    # To convert to YY if user keys in YYYY instead of YY
    if (len(spliced_year) > 2):
        spliced_year = spliced_year.strip("(")
        spliced_year = spliced_year.strip()
        spliced_year = spliced_year[2:4]

    time_arr = handle_time(time)
    start_time = time_arr[0]
    end_time = time_arr[1]

    start_string = "20{}-{}-{}T{}:{}:00+08:00".format(spliced_year, spliced_month, spliced_day, start_time[0], start_time[1])
    end_string = "20{}-{}-{}T{}:{}:00+08:00".format(spliced_year, spliced_month, spliced_day, end_time[0], end_time[1])

    return [start_string, end_string]

# Splices given date-time
def handle_time(s):
    arr = s.strip().split("-")
    return [parse_time(arr[0]), parse_time(arr[1])]

def parse_time(time):
    am_pm = time.strip()[-2:]
    arr = time.strip()[:-2].split(".")
    mins = arr[1]
    hr = arr[0]

    if (len(hr) < 2):
        hr = "0" + hr

    if (am_pm == "pm" and int(hr) != 12):
        hr = str(int(hr) + 12)

    return [hr, mins]

class Event:
    def __init__(self, date, time, cmi, agenda):
        self.date = date
        self.time = time
        self.cmi = cmi
        self.agenda = agenda

    def to_string(self):
        print(self.date, self.time, self.cmi, self.agenda)

bot.infinity_polling()