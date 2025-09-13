from .models import (
    DamageOperation, ModifyExportOperation, ModifySupplyOperation, ReturnDispatchOperation, ReturnSupplyOperation,
    SupplyOperation , ExportOperation, TransferOperation)
from .serializers import (  DamageOperationSerializer, ModifyExportOperationSerializer, ModifySupplyOperationSerializer, ReturnDispatchOperationSerializer,
                            ReturnSupplyOperationSerializer, SupplyOperationSerializer ,
                            ExportOperationSerializer, TransferOperationSerializer)
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser ,JSONParser
from rest_framework.permissions import IsAuthenticated
from core.services.mixins import UserPermissionsMixin
from django.db.models import Q


class SupplyOperationViewSet(UserPermissionsMixin,viewsets.ModelViewSet):
    """
    API endpoint for creating and viewing supply operations.
    
    To create a new supply operation, send a POST request with the
    operation data and a nested 'items' array.
    """
    permission_classes  = [IsAuthenticated]

    queryset = SupplyOperation.objects.all()

    warehouse_field_lookup = 'warehouse__in'

    serializer_class = SupplyOperationSerializer

    parser_classes = [ MultiPartParser, FormParser]




class ExportOperationViewSet(UserPermissionsMixin,viewsets.ModelViewSet):
    """
    API endpoint for creating and viewing Export operations.
    
    To create a new Export operation, send a POST request with the
    operation data and a nested 'items' array.
    """
    queryset   = ExportOperation.objects.all()
    permission_classes  = [IsAuthenticated]
    warehouse_field_lookup = 'warehouse__in'
    serializer_class = ExportOperationSerializer


class ReturnSupplyOperationViewSet(UserPermissionsMixin,viewsets.ModelViewSet):
    """
    API endpoint for creating and viewing returns against supply operations.
    """
    queryset = ReturnSupplyOperation.objects.all()
    permission_classes  = [IsAuthenticated]
    warehouse_field_lookup = 'original_operation__warehouse__in'
    serializer_class = ReturnSupplyOperationSerializer


class ReturnDispatchOperationViewSet(UserPermissionsMixin,viewsets.ModelViewSet):
    """
    API endpoint for creating and viewing returns against supply operations.
    """
    queryset = ReturnDispatchOperation.objects.all()
    warehouse_field_lookup = 'original_operation__warehouse__in'
    permission_classes  = [IsAuthenticated]

    serializer_class = ReturnDispatchOperationSerializer


class DamageOperationViewSet(UserPermissionsMixin,viewsets.ModelViewSet):
    """
    API endpoint for creating and viewing returns against supply operations.
    """
    queryset = DamageOperation.objects.all()
    warehouse_field_lookup = 'warehouse__in'
    serializer_class = DamageOperationSerializer
    permission_classes  = [IsAuthenticated]

class TransferOperationViewSet(UserPermissionsMixin, viewsets.ModelViewSet):
    """
    API endpoint for creating and viewing transfer operations.
    Permissions are handled specially for this view to check both
    'from_warehouse' and 'to_warehouse'.
    """
    queryset = TransferOperation.objects.all()
    serializer_class = TransferOperationSerializer
    permission_classes  = [IsAuthenticated]

    def get_queryset(self):
        queryset = super(UserPermissionsMixin, self).get_queryset() 
        user = self.request.user

        if not user.is_authenticated:
            return queryset.none()

        if user.is_superuser or user.user_type == 'Manager':
            return queryset

        if user.user_type == 'Employee':
            managed_warehouses_qs = user.managed_warehouses.all()
            if not managed_warehouses_qs.exists():
                return queryset.none()
            
            return queryset.filter(
                Q(from_warehouse__in=managed_warehouses_qs) | 
                Q(to_warehouse__in=managed_warehouses_qs)
            )
        
        return queryset.none()
    

class ModifySupplyOperationViewSet(UserPermissionsMixin,viewsets.ModelViewSet):
    queryset = ModifySupplyOperation.objects.all()
    warehouse_field_lookup = 'original_item_line__original_operation__warehouse__in'
    serializer_class = ModifySupplyOperationSerializer
    permission_classes  = [IsAuthenticated]

class ModifyExportOperationViewSet(UserPermissionsMixin,viewsets.ModelViewSet):
    queryset = ModifyExportOperation.objects.all()
    warehouse_field_lookup = 'original_item_line__original_operation__warehouse__in'
    serializer_class = ModifyExportOperationSerializer
    permission_classes  = [IsAuthenticated]


