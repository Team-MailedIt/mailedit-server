import requests

from django.db import transaction

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from project.settings.base import CLIENT_ID

User = get_user_model()

GOOGLE_ID_TOKEN_INFO_URL = "https://www.googleapis.com/oauth2/v3/tokeninfo"
GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def google_validate_id_token(*, id_token: str):
    # Reference: https://developers.google.com/identity/sign-in/web/backend-auth#verify-the-integrity-of-the-id-token
    response = requests.get(GOOGLE_ID_TOKEN_INFO_URL, params={"id_token": id_token})

    if not response.ok:
        raise ValidationError("id_token is invalid.")

    audience = response.json()["aud"]

    if audience != CLIENT_ID:
        raise ValidationError("Invalid audience.")

    return response.json()


def google_user_create(email, password=None, **extra_fields):
    extra_fields = {"is_staff": False, "is_superuser": False, **extra_fields}

    user = User(email=email, **extra_fields)

    if password:
        user.set_password(password)
    else:
        user.set_unusable_password()

    user.full_clean()
    user.save()

    return user


@transaction.atomic
def google_user_get_or_create(*, email: str, **extra_data):
    try:
        user = User.objects.get(email=email)
        if user.login_type != "GOOGLE":
            # 구글로 가입한 유저가 아니라면
            raise User.DoesNotExist
        return user, False

    except User.DoesNotExist:
        # 회원가입
        return google_user_create(email=email, **extra_data), True
