import binascii
from django.utils.encoding import force_str
from django.core.exceptions import ValidationError
from service.models import Group


def group_name_validator(value, user):
    group_names = Group.objects.filter(user_id=user.id).values_list("name", flat=True)
    match = value in group_names
    if match == True:
        raise ValidationError("Same group name is not allowed")


def group_color_validator(value, user):
    groups = Group.objects.filter(user_id=user.id)

    for group in groups:
        if group.color == value:
            raise ValidationError("Color must be different")


def color_hex_validator(value):
    if value[0] != "#":
        raise ValidationError("First character must be #")
    hex_value = force_str(value)[1:]
    try:
        binascii.unhexlify(hex_value)
    except (TypeError, binascii.Error):
        raise ValidationError("Only Hex value is allowed")
