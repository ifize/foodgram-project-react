from django.contrib.auth.tokens import PasswordResetTokenGenerator

GENERATOR = PasswordResetTokenGenerator()


def generate_token(user):
    return GENERATOR.make_token(user)


def check_token(user, token):
    return GENERATOR.check_token(user, token)
