from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from .views import PhoneVerifyConfirmView, ForgotPasswordView, ResetPasswordView

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh_token'),
    path("phone/request_verify_code/", views.PhoneVerifyRequestView.as_view(), name="phone_verify_request"),
    path("phone/confirm_verify_code/", PhoneVerifyConfirmView.as_view(), name="phone_verify_confirm"),

    path("forgot_password/", ForgotPasswordView.as_view(), name="forgot_password"),
    path("reset_password/", ResetPasswordView.as_view(), name="reset_password"),

]
