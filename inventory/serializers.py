from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator 
from rest_framework import serializers
from .models import Item , InventoryWarehouseitem ,Stations ,InventoryWarehouse



class WarehouseSerializer(serializers.ModelSerializer):
    """
    Serializer for the InventoryWarehouse model.
    Includes handling for the parent-child relationship.
    """
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    
    children_names = serializers.SerializerMethodField()
    storekeeper_name = serializers.CharField(source='storekeeper.full_name', read_only=True)

    class Meta:
        model = InventoryWarehouse
        fields = [
            'id', 
            'name', 
            'calssification', 
            'storekeeper', 
            'storekeeper_name', 
            'phone_warehouse', 
            'parent',         
            'parent_name',      
            'children_names'  ,
            'is_active'
        ]
        extra_kwargs = {
            'parent': {'required': False, 'allow_null': True},
            'calssification': {'required': True,}
        }


    def get_children_names(self, obj):
        """
        Custom method to get a list of names of the child warehouses.
        """
        return [child.name for child in obj.children.all()]

class WarehouseItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the InventoryWarehouseitem model, which represents the stock.
    This serializer is primarily for reading data, as stock levels are updated
    automatically by operations, not directly via the API.
    """

    # for write    
    warehouse = serializers.PrimaryKeyRelatedField(
        queryset=InventoryWarehouse.active.all()
    )
    item = serializers.PrimaryKeyRelatedField(
        queryset=Item.active.all()
    )

    # for read only
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    item_name = serializers.CharField(source='item.name', read_only=True)

    class Meta:
        model = InventoryWarehouseitem
        fields = [
            'id',
            'warehouse',          
            'warehouse_name',     
            'item',             
            'item_name',        
            'opening_balance',
            'current_quantity',
            'unit_of_measure',
            'last_updated'
        ]
        read_only_fields = ['current_quantity', 'last_updated']

class ItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the Item model. Handles creation, validation, and representation.
    """
    name = serializers.CharField(
        validators=[UniqueValidator(queryset=Item.objects.all())]
    )

    class Meta:
        model = Item
        fields = ['id', 'name' ,'is_active'] 

class StationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Stations model.
    """
    name = serializers.CharField(
        validators=[UniqueValidator(queryset=Stations.objects.all())]
    )

    class Meta:
        model = Stations
        fields = ['id', 'name', 'location' ,'is_active']