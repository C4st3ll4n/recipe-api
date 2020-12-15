from rest_framework import generics
from .serializers import UserSerializer
# Create your views here.


class CreateUserView(generics.CreateAPIView):
    """CREATE A NEW USER IN THE SYSTEM"""
    serializer_class = UserSerializer
