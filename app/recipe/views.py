from core.models import Tag
from recipe.serializers import TagSerializer
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


class TagViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get_queryset(self):
        """RETURN OBJECTS FOR THE AUTHENTICATED USER ONLY"""
        return self.queryset.filter(user=self.request.user).order_by("-name")
