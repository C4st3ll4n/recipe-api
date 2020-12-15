from django.contrib.auth import get_user_model

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
