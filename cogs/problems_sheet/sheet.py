# token.json is gitignored
# @Sirbot9988 you may be wondering why this file is formatted like this.
# it is formatted as a Discord cog, it's just a module that contains commands/tasks...
# So if you have any questions lmk
# Most of this code is useless if we move to an api
# TODO #2 Create an API to know when problem submissions are made and ditch the current method

import os
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from discord.ext import tasks, commands

# types
from typing import Dict, List

path = os.path.dirname(os.path.realpath(__file__))

# TODO #1 creds are recreated everytime any of the functions that depend on it are used.
# Creds constantly expire, I am not sure if this is working to refresh them.
def refresh_creds(path):
    token_path = f"{path}/token.json"

    SCOPES = ['https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/spreadsheets']

    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return creds

def to_index(letter: str) -> int:
    return 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.index(letter)

class Sheet(commands.Cog):

    # TODO there is definitely a way to look at the sheet
    # and know these key values without manually adding them here
    EDIT_URL = -1
    TIMESTAMP = to_index("A")

    CONFIRMED = to_index("R")
    CONFIRMED_COL = "R"
    INVALID = to_index("S")
    INVALID_COL = "S"

    LAST_COLUMN = "T"

    ID = '1ov98ZiRhY5E28uRjQdU76YG80-zkT0HtAMKgesphMbA'
    
    def __init__(self, bot):
        self.bot = bot
    
    @staticmethod
    def with_gdrive(f):
        def inner(*args, **kwargs):
            creds = refresh_creds(path)
            with build('drive', 'v3', credentials=creds) as gdrive:
                return f(gdrive, *args, **kwargs)

        return inner

    @staticmethod
    def with_spreadsheet(f):
        def inner(*args, **kwargs):
            creds = refresh_creds(path)
            with build('sheets', 'v4', credentials=creds).spreadsheets() as spreadsheet:
                return f(spreadsheet,*args, **kwargs)
            
        return inner

    # ONLY FUNCTION THAT HAS TO BE CALLED
    @tasks.loop(minutes=5)
    @staticmethod
    def update_sheet():
        Sheet.uncheck_edited_submissions()
        Sheet.delete_all_confirmed()
        Sheet.move_all_confirmed()
        # post or update problems in MongoDB
        Sheet.create_sheet_copy()

    @update_sheet.before_loop
    async def before_update_sheet(self):
        await self.bot.wait_until_ready()

    # TODO change to use batchUpdate
    @with_spreadsheet
    @staticmethod
    def uncheck_edited_submissions(spreadsheet) -> None:
        edited_submissions = Sheet.get_edited_submissions()
        for index in edited_submissions:
            index += 2
            range_ = f'{Sheet.CONFIRMED_COL}{index}:{Sheet.INVALID_COL}{index}'
            value_input_option = 'USER_ENTERED'

            value_range_body = {
                "range": f'{Sheet.CONFIRMED_COL}{index}:{Sheet.INVALID_COL}{index}',
                "majorDimension": 'ROWS',
                "values": [['FALSE', 'FALSE']]
            }

            request = spreadsheet.values().update(spreadsheetId=Sheet.ID,
                range=range_,
                valueInputOption=value_input_option,
                body=value_range_body)
            
            request.execute()

    # TODO should probably return the requests so that I do only one big batchUpdate
    @with_spreadsheet
    @staticmethod
    def delete_all_confirmed(spreadsheet) -> None:
        rows = Sheet.get_sheet_properties('Confirmed')['gridProperties']['rowCount']
        if rows == 1:
            return

        requests = {"requests": []}
        submitted_id = Sheet.get_sheet_properties('Confirmed')['sheetId']
        requests["requests"].append({
            "deleteDimension": {
                "range": {
                    "sheetId": submitted_id,
                    "dimension": "ROWS",
                    "startIndex": 1,
                    "endIndex": rows
                    }
                }
            })

        if requests['requests']:
            spreadsheet.batchUpdate(spreadsheetId=Sheet.ID, body=requests).execute()

    @with_spreadsheet
    @staticmethod
    # TODO should probably return the requests so that I do only one big batchUpdate
    def move_all_confirmed(spreadsheet) -> None:
        all_confirmed = Sheet.get_confirmed_submissions()
        requests = {"requests": []}

        confirmed_id = Sheet.get_sheet_properties('Confirmed')['sheetId']
        for values in all_confirmed:
            user_entered_values = Sheet.get_user_entered_values(values)
            requests["requests"].append({
                "appendCells": {
                    "sheetId": confirmed_id,
                    "rows": [
                        {
                            "values": user_entered_values
                            }],
                    "fields": "userEnteredValue"
                    }
                })

        if requests['requests']:
            spreadsheet.batchUpdate(spreadsheetId=Sheet.ID, body=requests).execute()

    @staticmethod
    def upload_to_mongo() -> None:
        # TODO LOOK ON DISCORD FOR THE POST API, ADD PROBLEMS MANUALLY IN FOR NOW
        pass

    @with_spreadsheet
    @staticmethod
    def create_sheet_copy(spreadsheet) -> None:
        values = Sheet.get_values_from('Submitted')
        with open(f"{path}/sheet_copy.txt", 'w') as file:
            file.write('\n'.join(['$$'.join(values[row] + [row]).replace('\n', '\\n') for row in values]))

    @with_spreadsheet
    @staticmethod
    def get_edited_submissions(spreadsheet) -> List[int]:
        old = Sheet.read_sheet_copy()
        new = Sheet.get_values_from('Submitted')
        list_new = list(new.keys())

        edited_submissions = []
        for problem in new:
            if problem in old:
                if (old[problem][Sheet.TIMESTAMP] != new[problem][Sheet.TIMESTAMP]
                    and (old[problem][Sheet.CONFIRMED] == 'TRUE'
                    or old[problem][Sheet.INVALID] == 'TRUE')):
                        
                    edited_submissions.append(list_new.index(problem))

        return edited_submissions

    @staticmethod
    def read_sheet_copy() -> Dict[str, List[str]]:
        with open(f"{path}/sheet_copy.txt", 'r') as file:
            return {line.split('$$')[Sheet.EDIT_URL].strip('\n'): line.split('$$')[:Sheet.EDIT_URL] for line in file.readlines()}

    @with_spreadsheet
    @staticmethod
    def get_confirmed_submissions(spreadsheet) -> List[List[str]]:
        all_values = Sheet.get_values_from('Submitted')
        confirmed_values = []
        for value in all_values:
            if all_values[value][Sheet.CONFIRMED] == 'TRUE':
                confirmed_values.append(all_values[value] + [value])

        return confirmed_values

    @with_spreadsheet
    @staticmethod
    def get_sheet_properties(spreadsheet, sheet_name: str) -> Dict:
        for sheet in spreadsheet.get(spreadsheetId=Sheet.ID).execute()['sheets']:
            if sheet['properties']['title'] == sheet_name:
                return sheet['properties']

    @staticmethod
    def get_user_entered_values(values: List[str]) -> List[Dict[str, Dict[str, str]]]:
        user_entered_values = []

        # skips confirmed, invalid, and edit url
        for val in values[:Sheet.CONFIRMED]:
            user_entered_values.append(
                {"userEnteredValue": {"stringValue": val}}
            )

        # appending edit_url
        user_entered_values.append(
            {"userEnteredValue": {"stringValue": values[Sheet.EDIT_URL]}}
        )

        return user_entered_values

    @with_spreadsheet
    @staticmethod
    def get_values_from(spreadsheet, sheet_name: str) -> Dict:
        rows = Sheet.get_sheet_properties(sheet_name)['gridProperties']['rowCount']
        if rows != 1:
            all_values = spreadsheet.values().get(spreadsheetId=Sheet.ID, range=f"{sheet_name}!A2:{Sheet.LAST_COLUMN}{rows}").execute()
            values = all_values['values']
            return {row[Sheet.EDIT_URL]: row[:Sheet.EDIT_URL] for row in values}

    @with_gdrive
    @staticmethod
    def read_io_file(gdrive, id: str) -> str:
        contents = gdrive.files().get_media(fileId=id).execute()
        return contents