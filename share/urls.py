from django.urls import path
from .views import UserSignupView
from .views import UserLogininView
from .views import VerifyEmailView

urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='user-signup'),
    path('login/', UserLogininView.as_view(), name='user-login'),
    path('verify/', VerifyEmailView.as_view(), name='verify-email'),
]
