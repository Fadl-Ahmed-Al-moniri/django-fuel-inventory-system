from rest_framework import serializers
from inventory.models import  InventoryWarehouseitem, Item
from operations.models import (
    DamageOperation, ExportOperation,
    ReturnSupplyOperation,SupplyOperation ,
    ReturnDispatchOperation, TransferOperation)
from operations.serializers import (DamagedItemSerializer, ExportOperationItemSerializer,
                                    ReturnDispatchItemSerializer,ReturnSupplyItemSerializer,
                                    SupplyOperationItemSerializer, TransferOperationItemSerializer,
                                    )




class ReportSupplySerializer(serializers.ModelSerializer):
    items = SupplyOperationItemSerializer(many=True, read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    stations_name = serializers.CharField(source='stations.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    
    class Meta:
        model = SupplyOperation
        fields = ['id', 'warehouse_name', 'operation_date', 'supplier_name','stations_name', 'items']


class ReportExportSerializer(serializers.ModelSerializer):

    items = ExportOperationItemSerializer(many=True, read_only=True)
    beneficiary_name = serializers.CharField(source='beneficiary.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    class Meta:
        model = ExportOperation
        fields = ['id', 'warehouse_name', 'operation_date', 'beneficiary_name', 'items']


class ReportReturnSupplySerializer(serializers.ModelSerializer):

    returned_items = ReturnSupplyItemSerializer(many=True, read_only=True)
    original_operation_id = serializers.IntegerField(source='original_operation.id', read_only=True)
    warehouse_name = serializers.CharField(source='original_operation.warehouse.name', read_only=True)
    stations_name = serializers.CharField(source='original_operation.stations.name', read_only=True)
    supplier_name = serializers.CharField(source='original_operation.supplier.name', read_only=True)
    class Meta:
        model = ReturnSupplyOperation
        fields = ['id', 'warehouse_name', 'operation_date', 'stations_name','supplier_name','original_operation_id', 'returned_items']


class ReportReturnExportSerializer(serializers.ModelSerializer):

    returned_items = ReturnDispatchItemSerializer(many=True, read_only=True)
    original_operation_id = serializers.IntegerField(source='original_operation.id', read_only=True)
    beneficiary_name = serializers.CharField(source='original_operation.beneficiary.name', read_only=True)
    warehouse_name = serializers.CharField(source='original_operation.warehouse.name', read_only=True)
    class Meta:
        model = ReturnDispatchOperation
        fields = ['id', 'warehouse_name', 'operation_date','beneficiary_name', 'original_operation_id', 'returned_items']


class ReportDamageSerializer(serializers.ModelSerializer):

    items = DamagedItemSerializer(many=True, read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    class Meta:
        model = DamageOperation
        fields = ['id', 'warehouse_name', 'operation_date', 'reason', 'items']


class ReportTransferSerializer(serializers.ModelSerializer):

    items = TransferOperationItemSerializer(many=True, read_only=True)
    from_warehouse = serializers.CharField(source='from_warehouse.name', read_only=True)
    to_warehouse = serializers.CharField(source='to_warehouse.name', read_only=True)
    class Meta:
        model = TransferOperation
        fields = ['id', 'from_warehouse', 'to_warehouse','operation_date', 'reason', 'items']



class WarehouseItemStatusSerializer(serializers.ModelSerializer):

    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    item_name = serializers.CharField(source='item.name', read_only=True)
    class Meta:
        model = InventoryWarehouseitem
        fields = ['id', 'warehouse_name', 'item_name', 'opening_balance', 'current_quantity', 'unit_of_measure', 'last_updated']




class ReturnsSubReportSerializer(serializers.Serializer):
    supply_returns = ReportReturnSupplySerializer(many=True, read_only=True)
    dispatch_returns = ReportReturnExportSerializer(many=True,read_only=True)


class GeneralWarehouseReportSerializer(serializers.Serializer):

    supplies = ReportSupplySerializer(many=True, read_only=True)
    dispatches = ReportExportSerializer(many=True, read_only=True)
    returns = ReturnsSubReportSerializer(read_only=True)
    damages = ReportDamageSerializer(many=True, read_only=True)

    def validate_warehouse(self, value):

        user = self.context['request'].user
        print(user)

        if user.is_superuser or user.user_type == 'Manager':
            return value 
        if user.user_type == 'Employee':
            if not user.managed_warehouses.filter(pk=value.pk).exists():
                raise serializers.ValidationError(
                    "You do not have permission to perform operations on this warehouse."
                )
            
            return value


class GeneralItemReportSerializer(serializers.Serializer):

    supplies = ReportSupplySerializer(many=True, read_only=True)
    dispatches = ReportExportSerializer(many=True, read_only=True)
    returns = ReturnsSubReportSerializer(read_only=True)
    damages = ReportDamageSerializer(many=True, read_only=True)
    transfer = ReportTransferSerializer(many =True ,read_only = True )

