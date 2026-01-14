import os, json
import random
from datetime import timedelta
from .serializers import RegisterSerializer, CountrySerializer, PhoneVerificationSerializer, \
    PhoneVerificationRequestSerializer, UserSerializer, LoginSerializer, ForgotPasswordSerializer, \
    ResetPasswordSerializer, LocationSerializer, ProfileSerializer
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.timezone import now

from .models import Location

User = get_user_model()

# Load countries JSON once
COUNTRIES_FILE = os.path.join(settings.BASE_DIR, 'authentication/data/countries.json')
with open(COUNTRIES_FILE, 'r', encoding='utf-8') as f:
    COUNTRIES = json.load(f)



def send_reset_code_email(user, code):
    subject = "Qent – Reset Your Password"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [user.email]

    text_content = f"This is your reset password code: {code}"

    html_content = render_to_string(
        "emails/reset_password.html",
        {
            "name": user.profile.full_name.split()[0] or user.username,
            "code": code,
            "expiry_minutes": 10,
            "year": now().year,
        }
    )

    email = EmailMultiAlternatives(
        subject,
        text_content,
        from_email,
        to
    )
    email.attach_alternative(html_content, "text/html")
    email.send()


class CountriesView(ListAPIView):
    """
    GET utils/countries/ → Returns list of countries
    """

    serializer_class = CountrySerializer

    def get_queryset(self):
        return COUNTRIES


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


class ProfileDetailsView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


class ProfileEditView(generics.UpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response(
            {"message": "Profile updated successfully", "data": response.data["data"]},
            status=status.HTTP_200_OK
        )


class LocationView(generics.ListAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {
                "message": 'Logged in successfully',
                **serializer.validated_data,
            },
            status=status.HTTP_200_OK
        )


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


class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        user = User.objects.get(email=email)

        # generate random 4-digit code
        code = str(random.randint(1000, 9999))
        user.profile.reset_code = code

        # create a short-lived access token for password reset
        token = RefreshToken.for_user(user).access_token
        token.set_exp(lifetime=timedelta(minutes=10))
        user.profile.reset_token = str(token)

        user.save()

        # Send Email
        send_reset_code_email(user, code)
        return Response(
            {
                "message": "Code sent to your email successfully",
                "code": code,  # for testing, in production you send via email
                "reset_token": str(token)
            },
            status=status.HTTP_200_OK
        )


class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        token = AccessToken(data['reset_token'])

        user = User.objects.get(id=token['user_id'])

        user.set_password(data["password"])
        user.profile.reset_code = None  # clear code
        user.profile.reset_token = None  # clear token
        user.save()

        return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)


class PhoneVerifyRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PhoneVerificationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone']
        user = request.user

        # create a short-lived access token for password reset
        token = RefreshToken.for_user(user).access_token
        token.set_exp(lifetime=timedelta(minutes=10))
        user.profile.reset_token = str(token)

        reset_code = str(random.randint(1000, 9999))
        user.profile.reset_code = reset_code
        user.profile.save()

        if user.profile.phone != phone:
            raise ValidationError({"message": "There is no account with the given number"})

        return Response(
            {"message": "Verification Code Sent", "code": reset_code, 'verify_token': str(token)},
            status=status.HTTP_200_OK
        )


class PhoneVerifyConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PhoneVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            token = AccessToken(data['verify_token'])
        except Exception:
            # raise a DRF validation error
            raise ValidationError({"message": "Invalid or expired token"})

        user = User.objects.get(id=token['user_id'])

        reset_code = data['code']

        if user.profile.reset_code != reset_code:
            raise ValidationError({"message": "Invalid code"})

        user.profile.phone_is_verified = True
        user.profile.reset_code = None
        user.profile.reset_token = None
        user.save()

        return Response({"user": UserSerializer(user).data,
                         "message": "Phone verified successfully",

                         }, status=status.HTTP_200_OK)
