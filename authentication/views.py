import os, json
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError
from .serializers import RegisterSerializer, CountrySerializer, PhoneVerificationSerializer, \
    PhoneVerificationRequestSerializer, UserSerializer, LoginSerializer
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

# Load countries JSON once
COUNTRIES_FILE = os.path.join(settings.BASE_DIR, 'authentication/data/countries.json')
with open(COUNTRIES_FILE, 'r', encoding='utf-8') as f:
    COUNTRIES = json.load(f)


class CountriesView(APIView):
    """
    GET utils/countries/ → Returns list of countries
    """

    serializer_class = CountrySerializer

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(COUNTRIES, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Create your views here.
class RegisterView(generics.CreateAPIView):
    """
        POST register → Create User
    """

    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            "message": "User created successfully",
            "tokens": {
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)


class PhoneVerifyRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PhoneVerificationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone']

        return Response(
            {"message": "Verification Code Sent", "phone": phone},
            status=status.HTTP_200_OK
        )


class PhoneVerifyConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PhoneVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.phone = serializer.validated_data['phone']
        user.phone_verified = True
        user.save()

        return Response({"user": UserSerializer(user).data,
                         "message": "Phone verified successfully",

                         }, status=status.HTTP_200_OK)
