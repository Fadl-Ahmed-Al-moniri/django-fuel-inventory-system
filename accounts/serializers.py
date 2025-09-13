from rest_framework import serializers
from django.contrib.auth.models import User
from .models import User, Supplier, Beneficiary
from rest_framework.validators import UniqueValidator 
from rest_framework import serializers
from .models import User, Supplier, Beneficiary

from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.exceptions import ValidationError as DjangoValidationError

class RegisterUserSerializer(serializers.ModelSerializer):

    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'password2', 'first_name', 'last_name', 'user_type', 'manager']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['user_type'] = user.user_type

        return token

    def validate(self, attrs):

        data = super().validate(attrs)

        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'full_name': self.user.full_name,
            'user_type': self.user.user_type,
            'manager':  self.user.manager.full_name if self.user.manager == True else None ,
        }
        
        return data




class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name','manager', 'user_type','password','is_active']

        extra_kwargs = {
            'password': {'write_only': True},
        }

    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()
            
        return user



class SupplierSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        validators=[UniqueValidator(queryset=Supplier.objects.all())]
    )

    class Meta:
        model = Supplier
        fields = ["id", "name", "phone_number",'is_active']
        extra_kwargs = {
            'phone_number': {'required': True,}
        }
    
class BeneficiarySerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        validators=[UniqueValidator(queryset=Beneficiary.objects.all())]
    )

    class Meta:
        model = Beneficiary
        fields = ["id", "name", "phone_number",'is_active']
        extra_kwargs = {
            'phone_number': {'required': True,}
        }
