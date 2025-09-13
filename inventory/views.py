from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from inventory.models import InventoryWarehouse, InventoryWarehouseitem, Item, Stations
from .serializers import ItemSerializer, StationSerializer,   WarehouseItemSerializer, WarehouseSerializer
from core.services.mixins import UserPermissionsMixin
from rest_framework.permissions import IsAuthenticated



class WarehouseViewSet(UserPermissionsMixin,viewsets.ModelViewSet):
    """
    API endpoint that allows warehouses to be viewed or edited.
    Supports creating hierarchical warehouses.
    """
    queryset = InventoryWarehouse.objects.all()
    warehouse_field_lookup = 'pk__in'
    serializer_class = WarehouseSerializer
    permission_classes  = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        print("request.data", request.data)
        requested_data = request.data.copy()
        requested_data['storekeeper'] = request.user.id
        serializer = self.get_serializer(data=requested_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("serializer.errors", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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



class WarehouseItemViewSet(UserPermissionsMixin,viewsets.ModelViewSet):
    """
    API endpoint that allows viewing warehouse stock levels.
    
    This endpoint is READ-ONLY because stock levels should only be
    modified automatically through creating new operations (Supply, Dispatch, etc.),
    not directly via the API.
    """
    queryset = InventoryWarehouseitem.objects.all()
    warehouse_field_lookup = 'warehouse__in'
    serializer_class = WarehouseItemSerializer
    filterset_fields = ['warehouse', 'item']
    permission_classes  = [IsAuthenticated]

class ItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing inventory items.
    
    Provides the following actions automatically:
    - `list` (GET /items/)
    - `create` (POST /items/)
    - `retrieve` (GET /items/{id}/)
    - `update` (PUT /items/{id}/)
    - `partial_update` (PATCH /items/{id}/)
    - `destroy` (DELETE /items/{id}/)
    """
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
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
    


class StationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing stations.
    
    Provides the following actions automatically:
    - `list` (GET /stations/)
    - `create` (POST /stations/)
    - `retrieve` (GET /stations/{id}/)
    - `update` (PUT /stations/{id}/)
    - `partial_update` (PATCH /stations/{id}/)
    - `destroy` (DELETE /stations/{id}/)
    """
    queryset = Stations.objects.all()
    serializer_class = StationSerializer
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