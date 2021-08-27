import os

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from data_manager.school import School


class GoogleSheet:
  SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


  def __init__(self, sheet_id, sheet_name):
    self.__sheet_id = sheet_id
    self.__sheet_name = sheet_name
    self.__service = None
    self.__values = []
    self.schools = {}

    self.__authenticate()
    self.__get_values()
    self.__parse_values_into_schools()

  
  def __authenticate(self):
    creds = None
    if os.path.exists('./credentials/token.json'):
      creds = Credentials.from_authorized_user_file('./credentials/token.json', GoogleSheet.SCOPES)
    if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
      else:
        flow = InstalledAppFlow.from_client_secrets_file('./credentials/client_secret.json', GoogleSheet.SCOPES)
        creds = flow.run_local_server(port=54321)
        with open('./credentials/token.json', 'w') as token:
            token.write(creds.to_json())

    self.__service = build('sheets', 'v4', credentials=creds)


  def __get_values(self):
    sheet = self.__service.spreadsheets()
    result = sheet.values().get(spreadsheetId=self.__sheet_id, range=self.__sheet_name).execute()
    self.__values = result.get('values', [])
    self.__values = self.__values[1:]


  def __parse_values_into_schools(self):
    for index, value in enumerate(self.__values):
      school = School(
        index=index,
        code=value[0],
        state=value[1],
        name=value[2],
        priority=value[3]
      )
      self.schools[index] = school
    

  def upload_schools(self):
    values = []
    for i in range(len(self.schools)):
      school = self.schools[i]
      values.append([school.color, school.last_scraped_message])

    sheet = self.__service.spreadsheets()
    sheet.values().update(
      spreadsheetId=self.__sheet_id,
      range='Sheet1!E2',
      valueInputOption='USER_ENTERED',
      body={
        'values': values
      }
    ).execute()
