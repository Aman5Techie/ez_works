from typing import Any
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status,views
from .models import User
from .serializers import UserRegistrationSerializer
from .serializers import AuthSerializer
from rest_framework import permissions
from knox.views import LoginView as KnoxLoginView
from knox.auth import TokenAuthentication
from django.contrib.auth import login
from django.core.mail import send_mail
from django.conf import settings
from cryptography.fernet import Fernet



class UserSignupView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = [TokenAuthentication]
    serializer_class = UserRegistrationSerializer
    
    """USING CRYPTOGRAPHY FOR VERIFICATION"""
    def __init__(self, **kwargs: Any) -> None:
         self.cipher = Fernet(settings.ENCRYPTION_KEY)
    
    def post(self, request, *args, **kwargs):
        verified_status = False
        
        """OPERATION USERS ARE VERIFIED"""
        if request.data.get("user_type") == 'operation':
            verified_status = True
            
        """COPY THE REQUEST DATA"""
        user_data = request.data.copy() 
        
        """ADD VERIFIED STATUS"""
        user_data["verified"] = verified_status 
                
        serializer = self.get_serializer(data=user_data)
        
        data = {
            "message" : "Email verified Login to get Token."
        }
        
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            user_type = serializer.validated_data.get("user_type")
            try:
                if user_type == "client":
                    
                    """SEND EMAIL TO CLIENT"""
                    verification_url = self.send_verification_email(email=email)
                    data["verification_url"] = verification_url
                    data["message"] = "Check your mail id for verification."
                    
            except Exception as e:

                return Response({
                    "detail" : "Please Try Again. "
                }, status=status.HTTP_400_BAD_REQUEST)
            
            """SAVE THE USER"""
            user = serializer.save()
            data["user_id"] = user.id
            data["email"] = user.email
            
            return Response(data, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def send_verification_email(self, email):
    
        encrypted_email = self.cipher.encrypt(email.encode()).decode()
        """URL TO VERIFY USER"""
        verification_url = f"http://127.0.0.1:8000/api/verify/?token={encrypted_email}"

        subject = "Verify Your Email Address"
        message = f"Hi \n\nPlease verify your email by clicking the link below:\n{verification_url}"
        
        """SEND MAIL TO USER SUCCESSFULLY"""
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        return verification_url

class UserLogininView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = [TokenAuthentication]

    def post(self, request, format = None):
        
        """SEND DATA TO SERIALIZER"""
        serializer = AuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        """GETTING USER FROM DATA"""
        user = serializer.validated_data['user']
    
        """LOGIN THE USER"""
        login(request, user)
        
        """RETURN TOKEN AND USER INFO"""
        return super().post(request, format=None)
    
class VerifyEmailView(views.APIView):
    permission_classes = [permissions.AllowAny]
    
    def __init__(self):
        self.cipher = Fernet(settings.ENCRYPTION_KEY)

    def get(self, request, *args, **kwargs):
        """GET TOKEN FORM PARAMS"""
        token = request.GET.get('token')
        
        if token:
            try:
                """EXTRACT THE EMAIL ID FROM TOKEN"""
                decrypted_email = self.cipher.decrypt(token.encode()).decode()
                
                """EXTRACT USER MODEL"""
                user = User.objects.get(email=decrypted_email)
                
                """MAKING HIM VERIFIED USER"""
                user.verified = True
                
                """SAVING USER"""
                user.save()

                return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "Token not provided."}, status=status.HTTP_400_BAD_REQUEST)
        

        