from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import telebot

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
bot = telebot.TeleBot("880940856:AAEmzUXVtMsES2xb6N2SK0UXDw6gYrhjHJQ")
data = []

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1PAgQN1Tm6_uI7w8opMIQ1daAiot3SNr0PG1UhQdDg14'
# SAMPLE_RANGE_NAME = 'Лист1!A1:D1'
SAMPLE_RANGE_NAME_TO_READ = 'Лист1!A1:C1'
# Имя, Фамилия, Отчество, Почта

def insertInfo(name, surname, patronymic, service):
    with open('rows_counter.txt', 'r') as f:
        strings = int(f.read())

    SAMPLE_RANGE_NAME = 'Лист1!A' + str(strings) + ':C' + str(strings)

    values = [
        [name, surname, patronymic],
    ]
    body = {
        'values': values,
    }

    result = service.spreadsheets().values().append(
        spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME,
        valueInputOption="RAW", body=body).execute()
    print('{0} cells appended.'.format(result \
                                       .get('updates') \
                                       .get('updatedCells')))

    with open('rows_counter.txt', 'w') as f:
        f.write(str(strings + 1))

creds = None
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
        creds = flow.run_local_server(port=5000)
        # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

service = build('sheets', 'v4', credentials=creds)

result = service.spreadsheets().values().get(
    spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME_TO_READ).execute()
rows = result.get('values', [])

@bot.message_handler(commands=['start'])
def start(message):
    msg = bot.send_message(message.chat.id, "Введите параметр \"{}\" ".format(rows[0][0]))
    data.clear()
    bot.register_next_step_handler(msg, detectFirst)

def detectFirst(message):
    data.append(message.text)
    msg = bot.send_message(message.chat.id, "Введите параметр \"{}\" ".format(rows[0][1]))
    bot.register_next_step_handler(msg, detectSurname)

def detectSurname(message):
    data.append(message.text)
    msg = bot.send_message(message.chat.id, "Введите параметр \"{}\" ".format(rows[0][2]))
    bot.register_next_step_handler(msg, detectEmail)

def detectEmail(message):
    data.append(message.text)
    insertInfo(data[0], data[1], data[2], service)
    bot.send_message(message.chat.id, "Данные добавлены!")

bot.polling()

# name = str(input("Введите параметр \"{}\" ".format(rows[0][0])))
# surname = str(input("Введите параметр \"{}\" ".format(rows[0][1])))
# patronymic = str(input("Введите параметр \"{}\" ".format(rows[0][2])))
# email = str(input("Введите параметр \"{}\" ".format(rows[0][3])))
#
# insertInfo(name, surname, patronymic, email, service)