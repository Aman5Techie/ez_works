from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import UploadedFile
import cloudinary.uploader
import random
import string
from rest_framework import status, views
from cryptography.fernet import Fernet
from django.http import HttpResponse
import requests
from knox.auth import TokenAuthentication
import base64
import hashlib

class FileUploadViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    ALLOWED_EXTENSIONS = ['pptx', 'docx', 'xlsx']

    def create(self, request):
        user = request.user
        
        """VALIDATING THE USERTYPE"""
        if(user.user_type != 'operation'):
            return Response({
                "msg" : "Client cannot Uploade."
            },status=status.HTTP_400_BAD_REQUEST)
                
        """VALIDATING THE FILE AND TYPE"""
        file = request.FILES.get('file')

        if not file:
            return Response({'error': 'No file provided.'}, status=400)

        file_extension = file.name.split('.')[-1]
        if file_extension not in self.ALLOWED_EXTENSIONS:
            return Response({'error': 'Invalid file type. Only pptx, docx, and xlsx are allowed.'}, status=400)

        """UPLOADING FILE TO CLOUDINARY"""
        try:
            cloudinary_response = cloudinary.uploader.upload(file,resource_type='raw' )
            file_url = cloudinary_response['secure_url']
        except Exception as e:
            return Response({'error': str(e)}, status=500)

        """GENERATE UNIQUE ID FOR FILE"""

        unique_id = self.generate_unique_id()
        
        """MAKE OBJECT OF UPLOADFILE"""
        uploaded_file = UploadedFile.objects.create(  
            unique_id=unique_id,
            file_url=file_url,
            original_file_name=file.name
        )

        return Response({
            'unique_id': unique_id,
            'file_url': file_url,
            'original_file_name': file.name,
            'message': 'File uploaded successfully.'
        }, status=201)

    def generate_unique_id(self):
        """GENERATE UNIQUE 6 DIGIT STRING"""
        while True:
            unique_id = ''.join(random.choices(string.digits, k=6))
            if not UploadedFile.objects.filter(unique_id=unique_id).exists():
                return unique_id


class FileDownloadViewSet(views.APIView):
    """ENCYPT THE DOWNLOAD URL"""
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def get(self,request): 
        """VALIDATING FILE ID"""
        file_id = self.request.query_params.get("file_id",False)
        
        if not file_id:
            return Response({
                'message': 'Please provide file_id in params.'
            }, status=400)
        
        """VALIDATING THE FILE ID"""
        try:
            file = UploadedFile.objects.get(unique_id = file_id)
        except:
            return Response({
                'message': 'Invalid File Id.'
            }, status=400)
            
        file_url = file.file_url
        
        """ENCRYPT THE URL SO ONLY REQUESTED USER CAN ACCESS"""
        encrypted_url = self.encrypt_file_url(file_url, request.user.email)
        
        
        return Response({
            'encrypted_file_url': f"http://127.0.0.1:8000/api/download_file/{encrypted_url}",
            'message': 'File URL encrypted successfully.'
        }, status=200)
        
    def encrypt_file_url(self, file_url, user_email):
        """CREATE HASH BASED ON USER EMAIL"""
        key = hashlib.sha256(user_email.encode()).digest()
        fernet = Fernet(base64.urlsafe_b64encode(key))
        
        encrypted_url = fernet.encrypt(file_url.encode())
        return encrypted_url.decode()
    

class FileDecryptViewSet(views.APIView):
    """DECRYPT THE DOWNLOAD URL"""
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request,url):
        """VALIDATING ENCRYPTED URL"""
        encrypted_url = url

        if not encrypted_url:
            return Response({
                'message': 'Please provide url in params.'
            }, status=400)

        # Decrypt the file_url using the user's email
        try:
            """EXTRACT DECRYTP URL"""
            decrypted_url = self.decrypt_file_url(encrypted_url, request.user.email)
            """DOWNLOAD FILE TO USER SYSTEM"""
            return self.download_file(decrypted_url)
        except Exception as e:
            return Response({
                'message': 'Not authorized to download this file.'
            }, status=400)
    
    def decrypt_file_url(self, encrypted_url, user_email):
        
        key = hashlib.sha256(user_email.encode()).digest()
        fernet = Fernet(base64.urlsafe_b64encode(key))
        
        decrypted_url = fernet.decrypt(encrypted_url.encode())
        return decrypted_url.decode()
    
    def download_file(self, file_url):
        
        response = requests.get(file_url, stream=True)

        if response.status_code == 200:
            
            file_response = HttpResponse(
                response.content,
                content_type='application/octet-stream'
            )
           
            file_response['Content-Disposition'] = f'attachment; filename="{file_url.split("/")[-1]}"'
            return file_response
        else:
            return Response({
                'message': 'Failed to download the file.'
            }, status=404)
