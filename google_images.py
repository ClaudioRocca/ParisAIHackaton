import os
import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

scopes=['https://www.googleapis.com/auth/photoslibrary.readonly']

creds = None

if os.path.exists('/token.json'):
    creds = Credentials.from_authorized_user_file('_secrets_/token.json', scopes)

from google.auth.transport.requests import AuthorizedSession
authed_session = AuthorizedSession(creds)
        