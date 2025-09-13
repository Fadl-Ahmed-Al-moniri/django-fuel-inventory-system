from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import User, Supplier, Beneficiary
from .serializers import UserSerializer, SupplierSerializer, BeneficiarySerializer
from core.services.create_response import create_response 
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import RegisterUserSerializer, CustomTokenObtainPairSerializer
from .models import User
from rest_framework_simplejwt.views import TokenObtainPairView

class RegisterUserView(generics.CreateAPIView):

    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterUserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"message": "User created successfully. Please log in."},
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class CustomTokenObtainPairView(TokenObtainPairView):

    serializer_class = CustomTokenObtainPairSerializer
    


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing users.
    
    Provides the following actions automatically:
    - `list` (GET /users/)
    - `create` (POST /users/)
    - `retrieve` (GET /users/{id}/)
    - `update` (PUT /users/{id}/)
    - `partial_update` (PATCH /users/{id}/)
    - `destroy` (DELETE /users/{id}/)
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes  = [IsAuthenticated]


    def get_queryset(self):
        user = self.request.user
        base_queryset = super().get_queryset()
        if user.is_superuser or user.user_type == 'Manager':
            return base_queryset
        return base_queryset.filter(is_active=True)
        
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class SupplierViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing suppliers.
    """
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes  = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        base_queryset = super().get_queryset()
        if user.is_superuser or user.user_type == 'Manager':
            return base_queryset
        return base_queryset.filter(is_active=True)
    
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)

class BeneficiaryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing beneficiaries.
    """
    queryset = Beneficiary.objects.all()
    serializer_class = BeneficiarySerializer
    permission_classes  = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        base_queryset = super().get_queryset()
        if user.is_superuser or user.user_type == 'Manager':
            return base_queryset
        return base_queryset.filter(is_active=True)
    
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
