from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ungettext_lazy as _
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """SERIALIZER FOR THE USER OBJECT"""

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}, }

    def create(self, validated_data):
        """CREATE A NEW USER WITH ENCRYPTED PASSWORD AND RETURN IT"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """SERIALIZER FOR THE USER AUTHENTICATION"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """VALIDATE AND AUTHENTICATE THE USER"""
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email, password=password
        )

        if not user:
            msg = _("Unable to authenticate the user", plural='users')
            raise serializers.ValidationError(msg, code='authenticate')

        attrs['user'] = user
        return attrs
