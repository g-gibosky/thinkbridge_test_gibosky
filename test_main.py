from __future__ import print_function
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import google.auth
import spacy




class NPLGDRIVER():
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
    cred = None
    service = None
    def __init__(self, *args, **kwargs):
        super(NPLGDRIVER, self).__init__(*args, **kwargs)
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())
        try:
            self.service = build('drive', 'v3', credentials=self.creds)
        except Exception:
            print('Error', Exception)

    def load_documents(self, query):
        query = '' if query == '' else self.build_query(query)
        results = self.service.files().list(q=query, fields='files(id, name)').execute()
        return results.get('files', [])
    
    def build_query(self, query='The quick brown fox jumps over the lazy dog'):
        nlp = spacy.load('en_core_web_sm')
        doc = nlp(query)
        result_query = ''
        if len(doc) == 1:
            result_query += f'name = "{doc[0].text}"'
        else:
            result_query = " or ".join(f"name contains '{name.text.strip()}'" for name in doc)
        return f'{result_query} and trashed=false'


def main():
    try:
        # Call the Drive v3 API
        g_drive = NPLGDRIVER()
        items = g_drive.load_documents(query="Windows is from Microsoft")
        if not items:
            print('No files found.')
            return
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    main()
    