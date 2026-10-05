import re

from rest_framework import serializers

_CAPITAL_LETTER = re.compile(r'[A-Z]')
_SPECIAL_CHARACTER = re.compile(r'[^A-Za-z0-9]')


def validate_client_password(password):
    if password is None or password == '':
        raise serializers.ValidationError('Password is required.')

    if len(password) < 6:
        raise serializers.ValidationError('Password must be at least 6 characters long.')

    if not _CAPITAL_LETTER.search(password):
        raise serializers.ValidationError('Password must contain at least one capital letter.')

    if not _SPECIAL_CHARACTER.search(password):
        raise serializers.ValidationError('Password must contain at least one special character.')

    return password
