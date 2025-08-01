from django.urls import path
from .views import LoginView, LogoutView, RefreshTokenView, UserInfoView, ValidateTokenView

urlpatterns = [
    path('login/', LoginView.as_view(), name='auth-login'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('refresh/', RefreshTokenView.as_view(), name='auth-refresh'),
    path('me/', UserInfoView.as_view(), name='auth-me'),
    path('validate/', ValidateTokenView.as_view(), name='auth-validate'),
] 