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

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserSelfSerializer(UserSerializer):
    class Meta:
        model = User
        fields = FIELDS
