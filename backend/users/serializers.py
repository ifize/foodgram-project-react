from rest_framework import serializers

from django.contrib.auth import get_user_model


User = get_user_model()

FIELDS = (
    'email',
    'username',
    'first_name',
    'last_name',
    'password'
)


class UserSignUpSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = FIELDS

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError("Choose another name")
        return value


class UserSelfSerializer(UserSerializer):
    class Meta:
        model = User
        fields = FIELDS
