from django.core.mail import EmailMessage, BadHeaderError


def create_email(to, subject, message_text):
    return EmailMessage(subject=subject, body=message_text, to=[to])


def send_email(email):
    try:
        email.send()
        print(f'Message sent to {email.to}.')
        return email
    except BadHeaderError as error:
        print('An error occurred: %s' % error)


def send_verification_link(user_email, verification_link):
    mail_content = f"MailedIt! 회원 가입을 환영합니다.\n\n아래 링크를 통해 이메일 주소를 인증하세요.\n링크는 72시간 동안만 유효하며, 72시간 이후에는 새 링크를 발급받아 인증해야 합니다.\n\n{verification_link}\n\n감사합니다.\nTeam MailedIt\n\n본 이메일은 발신 전용으로, 수신 메일 확인이 어렵습니다. "
    email = create_email(user_email, "MailedIt! 회원 가입을 환영합니다", mail_content)
    send_email(email)
