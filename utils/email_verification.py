import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient import errors
from email.message import EmailMessage
import base64


SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def gmail_authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=65275, approval_prompt="force", access_type="offline")
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)


def create_message(sender, to, subject, message_text):
    message = EmailMessage()
    message["From"] = sender
    message["To"] = to
    message["Subject"] = subject
    message.set_content(message_text)
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode('utf8')}


def send_message(service, user_id, message):
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def send_verification_link(user_email, verification_link):
    service = gmail_authenticate()
    mail_content = f"MailedIt! 회원 가입을 환영합니다.\n\n아래 링크를 통해 이메일 주소를 인증하세요.\n링크는 1시간 동안만 유효하며, 1시간 이후에는 새 링크를 발급받아 인증해야 합니다.\n\n{verification_link}\n\n감사합니다.\nTeam MailedIt\n\n본 이메일은 발신 전용으로, 수신 메일 확인이 어렵습니다. "
    message = create_message("mailedit.noreply@gmail.com", user_email, "MailedIt! 회원 가입을 환영합니다", mail_content)
    send_message(service, "", message)
