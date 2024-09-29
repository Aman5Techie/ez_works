from rest_framework import serializers
from django.contrib.auth import  authenticate
from .models import User

class AuthSerializer(serializers.Serializer):
    '''serializer for the user authentication object'''
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )    
    
    def validate(self, attrs):
        """GET EMAIL AND PASS FROM USER"""
        email = attrs.get('email')
        password = attrs.get('password')
        
        """AUTHENTICATE USER BASED ON PASSWORD"""
        user = authenticate(
            request=self.context.get('request'),
            email=email,
            password=password,
        )

        """INCORRECT CREDENTIALS"""
        if not user:
            msg = ('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authentication')
        
        """IF CLIENT IS NOT VERIFIED"""
        if not user.verified:
            msg = ('Please verifiy you email first')
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email','username', 'user_type', 'password',"verified"]

    def create(self, validated_data):
        """USERNAME PROVIDED ELSE TOOK FROM EMAIL ID"""
        username = validated_data.get('username', f'{validated_data["email"].split("@")[0]}')
        
        user = User(
            email=validated_data['email'],
            username=username,
            user_type=validated_data['user_type'],
            verified= validated_data["verified"]
        )
        
        """SAVE HASH PASSWORD"""
        user.set_password(validated_data['password'])  
        user.save()
        return user
    
class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model without password field."""

    class Meta:
        model = User
        fields = ['username', 'email', 'username', 'user_type', 'verified']
    