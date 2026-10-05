from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from freezer_data.serializers import ClientLoginSerializer, ClientRegisterSerializer


class ObtainAuthTokenView(APIView):
    """Issue API tokens from email and password. Public so clients can authenticate."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Auth'],
        summary='Log in',
        description=(
            'Exchange email (as `username`) and password for an API token. '
            'Password must be at least 6 characters with one capital letter and one special character. '
            'Use `Authorization: Token <token>` on other endpoints.'
        ),
        request=ClientLoginSerializer,
        responses={200: None},
    )
    def post(self, request):
        serializer = ClientLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
        )
        if user is None:
            return Response(
                {'detail': 'Invalid email or password.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})


@extend_schema(
    tags=['Auth'],
    summary='Client sign up',
    description=(
        'Create a client account with email and password. Returns an API token. '
        'Password must be at least 6 characters with one capital letter and one special character.'
    ),
    request=ClientRegisterSerializer,
    responses={201: None},
)
@api_view(['POST'])
@permission_classes([AllowAny])
def client_register(request):
    serializer = ClientRegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    token, _ = Token.objects.get_or_create(user=user)
    return Response(
        {
            'token': token.key,
            'user_id': user.id,
            'email': user.email,
        },
        status=status.HTTP_201_CREATED,
    )
