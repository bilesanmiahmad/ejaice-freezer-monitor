from drf_spectacular.utils import extend_schema
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny


class ObtainAuthTokenView(ObtainAuthToken):
    """Issue API tokens from username/password. Public so clients can authenticate."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Auth'],
        summary='Obtain API token',
        description='Exchange Django username and password for a token. Use `Authorization: Token <token>` on other endpoints.',
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
