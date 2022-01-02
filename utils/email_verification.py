import httplib2
import os
from oauth2client import client, tools, file
import base64
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apiclient import errors, discovery
from project.settings.base import BASE_DIR


SENDER = "mailedit.noreply@gmail.com"


def get_credentials():
    credential_path = os.path.join(BASE_DIR, "credentials.json")
    store = file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        CLIENT_SECRET_FILE = "client-secret.json"
        APPLICATION_NAME = "Gmail API Python Send Email"
        SCOPES = "https://www.googleapis.com/auth/gmail.send"
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
    return credentials


def create_message_and_send(sender, to, subject, message_content):
    credentials = get_credentials()
    http = httplib2.Http()
    http = credentials.authorize(http)
    service = discovery.build("gmail", "v1", http=http)
    message = create_message(sender, to, subject, message_content)
    send_message(service, "me", message)


def create_message(sender, to, subject, message_content):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = to
    message.attach(MIMEText(message_content, "plain"))
    raw_message_no_attachment = base64.urlsafe_b64encode(message.as_bytes())
    raw_message_no_attachment = raw_message_no_attachment.decode()
    body = {"raw": raw_message_no_attachment}
    return body


def send_message(service, user_id, body):
    try:
        message_sent = (
            service.users().messages().send(userId=user_id, body=body).execute()
        )
        message_id = message_sent["id"]
        print(f"Message sent. Message Id: {message_id}")
    except errors.HttpError as error:
        print(f"An error occurred: {error}")


def send_verification_link(user_email, verification_link):
    mail_content = f"안녕하세요. MailedIt! 회원 가입을 환영합니다.\n\n아래 링크를 통해 이메일 주소를 인증하세요.\n링크는 72시간 동안만 유효하며, 72시간 이후에는 새 링크를 발급받아 인증해야 합니다.\n\n{verification_link}\n\n감사합니다.\nTeam MailedIt\n\n(본 이메일은 발신 전용으로, 수신 메일 확인이 어렵습니다.)"
    create_message_and_send(SENDER, user_email, "MailedIt! 회원 가입을 환영합니다.", mail_content)
