import os
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from discord.ext import commands

# types
from typing import Dict, List

class SheetManagement(commands.Cog):
    path = os.path.dirname(os.path.realpath(__file__))
    token_path = f"{path}/token.json"

    SCOPES = ['https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    ID = '1ov98ZiRhY5E28uRjQdU76YG80-zkT0HtAMKgesphMbA'

    def __init__(self, bot):
        self.bot = bot

    def with_gdrive(f):
        def inner(*args, **kwargs):
            with build('drive', 'v3', credentials=creds) as gdrive:
                return f(gdrive, *args, **kwargs)

        return inner

    def with_spreadsheet(f):
        def inner(*args, **kwargs):
            with build('sheets', 'v4', credentials=creds).spreadsheets() as spreadsheet:
                return f(spreadsheet,*args, **kwargs)
            
        return inner

    # TODO change to use batchUpdate
    @with_spreadsheet
    def uncheck_edited_submissions(spreadsheet) -> Dict:
        edited_submissions = get_edited_submissions()
        for index in edited_submissions:
            index =+ 1
            range_ = f'H{index}:I{index}'
            # How the input data should be interpreted.
            value_input_option = 'USER_ENTERED'

            value_range_body = {
                "range": f'H{index}:I{index}',
                "majorDimension": 'ROWS',
                "values": [['FALSE', 'FALSE']]
            }

            request = spreadsheet.values().update(spreadsheetId=ID, range=range_, valueInputOption=value_input_option, body=value_range_body)
            response = request.execute()

    @with_spreadsheet
    def get_edited_submissions(spreadsheet):
        old = read_sheet_copy()
        new = get_values_from('Submitted')
        list_new = list(new.keys())

        TIMESTAMP = 0
        CONFIRMED = 7
        INVALID = 8
        edited_submissions = []
        for problem in new:
            if problem in old:
                if old[problem][TIMESTAMP] != new[problem][TIMESTAMP]:
                    if old[problem][CONFIRMED] == 'TRUE' or old[problem][INVALID] == 'TRUE':
                        edited_submissions.append(list_new.index(problem))

        return edited_submissions

    def read_sheet_copy() -> Dict:
        with open(f"{path}/sheet_copy.txt", 'r') as file:
            return {line.split('$$')[-1].strip('\n'): line.split('$$')[:-1] for line in file.readlines()}

    @with_spreadsheet
    def create_sheet_copy(spreadsheet):
        values = get_values_from('Submitted')
        with open(f"{path}/sheet_copy.txt", 'w') as file:
            file.write('\n'.join(['$$'.join(values[row] + [row]) for row in values]))

    @with_spreadsheet
    def get_confirmed_submissions(spreadsheet) -> List[List[str]]:
        all_values = get_values_from('Submitted')
        CONFIRMED = 7
        confirmed_values = []
        for value in all_values:
            if all_values[value][CONFIRMED] == 'TRUE':
                confirmed_values.append(all_values[value] + [value])

        return confirmed_values

    @with_spreadsheet
    def get_values_from(spreadsheet, sheet_name: str) -> Dict:
        rows = get_sheet_properties(sheet_name)['gridProperties']['rowCount']
        if rows != 1:
            all_values = spreadsheet.values().get(spreadsheetId=ID, range=f"{sheet_name}!A2:J{rows}").execute()
            values = all_values['values']
            return {row[-1]: row[:-1] for row in values}

    @with_spreadsheet
    def get_sheet_properties(spreadsheet, sheet_name: str) -> Dict:
        for sheet in spreadsheet.get(spreadsheetId=ID).execute()['sheets']:
            if sheet['properties']['title'] == sheet_name:
                return sheet['properties']

    @with_spreadsheet
    # TODO should probably return the requests so that I do only one big batchUpdate
    def move_all_confirmed(spreadsheet) -> None:
        all_confirmed = get_confirmed_submissions()
        requests = {"requests": []}

        confirmed_id = get_sheet_properties('Confirmed')['sheetId']
        for value in all_confirmed:
            requests["requests"].append({
                "appendCells": {
                    "sheetId": confirmed_id,
                    "rows": [
                        {"values": [
                            {"userEnteredValue": {"stringValue": value[0]}},
                            {"userEnteredValue": {"stringValue": value[1]}},
                            {"userEnteredValue": {"stringValue": value[2]}},
                            {"userEnteredValue": {"stringValue": value[3]}},
                            {"userEnteredValue": {"stringValue": value[4]}},
                            {"userEnteredValue": {"stringValue": value[5]}},
                            {"userEnteredValue": {"stringValue": value[6]}},
                            {"userEnteredValue": {"stringValue": value[9]}}]
                            }],
                    "fields": "userEnteredValue"
                    }
                })

        spreadsheet.batchUpdate(spreadsheetId=ID, body=requests).execute()

    # TODO should probably return the requests so that I do only one big batchUpdate
    @with_spreadsheet
    def delete_all_confirmed(spreadsheet) -> None:
        rows = get_sheet_properties('Confirmed')['gridProperties']['rowCount']
        if rows == 1:
            return

        requests = {"requests": []}
        submitted_id = get_sheet_properties('Confirmed')['sheetId']
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
            spreadsheet.batchUpdate(spreadsheetId=ID, body=requests).execute()

    @with_gdrive
    def read_io_file(gdrive, id: str) -> str:
        contents = gdrive.files().get_media(fileId=id).execute()
        return contents

    get_edited_submissions()
    delete_all_confirmed()
    move_all_confirmed()
    create_sheet_copy()