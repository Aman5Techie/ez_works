from rest_framework import status
from rest_framework.test import APITestCase
from .models import User
from django.core import mail
from cryptography.fernet import Fernet
from django.conf import settings

class UserViewsTest(APITestCase):
    def setUp(self):
        self.cipher = Fernet(settings.ENCRYPTION_KEY)

    def test_user_signup_with_client_type(self):
        url = '/api/signup/'  
        data = {
            'email': 'testclient@example.com',
            'password': 'password123',
            'user_type': 'client'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 1)  
        self.assertIn('Verify Your Email Address', mail.outbox[0].subject)

    def test_user_signup_with_operation_type(self):
        url = '/api/signup/'   
        data = {
            'email': 'testoperation@example.com',
            'password': 'password123',
            'user_type': 'operation'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 0)  

    def test_verify_email(self):
      
        user = User.objects.create_user(email='testverify@example.com', password='password123', user_type='client')
        user.save()

        
        encrypted_email = self.cipher.encrypt(user.email.encode()).decode()
        url = f'/api/verify/?token={encrypted_email}'  

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get(email=user.email).verified, True)

    def test_login_user(self):
     
        user = User.objects.create_user(email='testlogin@example.com', password='password123', user_type='client',verified=True)
        user.save()

        url = '/api/login/'  
        data = {
            'email': 'testlogin@example.com',
            'password': 'password123',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
