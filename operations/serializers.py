import json
from marshmallow import ValidationError
from rest_framework import serializers
from django.db import transaction
from accounts.models import Supplier
from inventory.models import InventoryWarehouse, InventoryWarehouseitem, Stations
from operations.models import (
    DamageOperation, DamageOperationItem, ExportOperation,
    ExportOperationItem, ModifyExportOperation, ModifySupplyOperation, OperationAttachment, ReturnSupplyOperation,
    ReturnSupplyOperationItem, SupplyOperation, SupplyOperationItem ,
    ReturnDispatchOperation,ReturnDispatchOperationItem,
    TransferOperation, TransferOperationItem)

class OperationAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationAttachment
        fields = ['id', 'file', 'description', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']

class SupplyOperationItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    effective_quantity = serializers.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        read_only=True
    )
    class Meta:
        model = SupplyOperationItem
        fields = ['id','item','item_name', 'quantity','returned_quantity','effective_quantity'] 

class SupplyOperationSerializer(serializers.ModelSerializer):

    items = serializers.CharField(write_only=True, required=True)
    items_details = SupplyOperationItemSerializer(many=True, read_only=True, source='items')

    warehouse = serializers.PrimaryKeyRelatedField(
        queryset=InventoryWarehouse.active.all()
    )

    supplier = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.active.all()
    )
    stations = serializers.PrimaryKeyRelatedField(
        queryset=Stations.active.all(),
    )
    uploaded_attachments = serializers.ListField(
        child=serializers.FileField(allow_empty_file=False, use_url=False),
        write_only=True,
        required=False )
    

    recipient_user_name =serializers.CharField(source='recipient_user.full_name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    item_name = serializers.CharField(source='item.name', read_only=True,)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    stations_name = serializers.CharField(source='stations.name', read_only=True)
    show_attachments = OperationAttachmentSerializer(many=True, read_only=True)
    

    class Meta:
        model = SupplyOperation
        fields = [
            'id', 
            'warehouse', 
            'supplier', 
            'stations', 
            'operation_date',
            'items',
            'items_details',
            'paper_ref_number',
            'supply_bon_number',
            'delivere_job_name',
            'delivere_job_number',
            'recipient_user',
            'recipient_user_name',
            'operation_statement',
            'operation_descrabtion',
            'show_attachments', 
            'uploaded_attachments' ,
            'warehouse_name' ,
            'item_name' ,
            'stations_name' ,
            'supplier_name' ,
        ]
        extra_kwargs = {
            'stations': {'required': True,} ,
            'operation_statement': {'required': True,} ,
            'operation_descrabtion': {'required': True,} 
        }

    def validate_warehouse(self, value):
        user = self.context['request'].user
        print(f">>>>>>>>>>>>>>>>>>>>>>>>>{user}")

        if user.is_superuser or user.user_type == 'Manager':
            print(">>>>>>>>>>>>>>>>>>>>>>>>>Manager")
            return value 
        if user.user_type == 'Employee':

            if not user.managed_warehouses.filter(pk=value.pk).exists():
                raise serializers.ValidationError(
                    "You do not have permission to perform operations on this warehouse."
                )
            print(">>>>>>>>>>>>>>>>>>>>>>>>>Employee")
            
            return value

        raise serializers.ValidationError("You do not have permission to perform this action.")

    def create(self, validated_data):
        uploaded_files = validated_data.pop('uploaded_attachments', [])
        items_json_string = validated_data.pop('items')         
        try:
            items_data = json.loads(items_json_string)
        except json.JSONDecodeError:
            raise serializers.ValidationError({'items': 'Invalid JSON format.'})

        if not isinstance(items_data, list) or not items_data:
            raise serializers.ValidationError({'items': 'Items must be a non-empty list.'})


        item_serializer = SupplyOperationItemSerializer(data=items_data, many=True)
        if not item_serializer.is_valid():
            raise serializers.ValidationError({'items': item_serializer.errors})
        validated_items = item_serializer.validated_data
        try:
            user = self.context['request'].user
            print(f"validated_data::: {user}")
            with transaction.atomic():
                supply_operation = SupplyOperation.objects.create(**validated_data)
                supply_operation.recipient_user = user
                for item_data in validated_items:
                    SupplyOperationItem.objects.create(operation=supply_operation, **item_data)
                for file in uploaded_files:
                    OperationAttachment.objects.create(
                        supply_operation=supply_operation, 
                        file=file
                    )
                return supply_operation
        except Exception as e:
            raise serializers.ValidationError(str(e))

class ExportOperationItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the items within a dispatch/export operation.
    """
    item_name = serializers.CharField(source='item.name', read_only=True)
    effective_quantity = serializers.DecimalField(
        # source='effective_quantity', 
        max_digits=15, 
        decimal_places=2, 
        read_only=True
    )
    class Meta:
        model = ExportOperationItem
        fields = ['id','item','item_name', 'quantity','returned_quantity','effective_quantity'] 

class ExportOperationSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    items = serializers.CharField(write_only=True, required=True)
    items_details = ExportOperationItemSerializer(many=True, read_only=True, source='items')
    show_attachments = OperationAttachmentSerializer(many=True, read_only=True)
    delivere_user_name =serializers.CharField(source='delivere_user.full_name', read_only=True)
    uploaded_attachments = serializers.ListField(
        child=serializers.FileField(allow_empty_file=False, use_url=False),
        write_only=True,
        required=False )
    beneficiary_name = serializers.CharField(source='beneficiary.name', read_only=True)
    
    class Meta:
        model = ExportOperation
        fields = [
            'id', 
            'warehouse', 
            'warehouse_name', 
            'beneficiary', 
            'beneficiary_name', 
            'operation_date',
            'items',  
            'items_details',  
            'paper_ref_number',
            'delivere_user',
            'delivere_user_name',
            'recipient_name',
            'recipient_job_number',
            'operation_statement',
            'operation_descrabtion',
            "date_transfer",
            "date_actual_transfer",
            'show_attachments', 
            'uploaded_attachments' 
        ]

    def validate_warehouse(self, value):
        user = self.context['request'].user

        if user.is_superuser or user.user_type == 'Manager':
            return value 
        if user.user_type == 'Employee':

            if not user.managed_warehouses.filter(pk=value.pk).exists():
                raise serializers.ValidationError(
                    "You do not have permission to perform operations on this warehouse."
                )
            
            return value
        
        raise serializers.ValidationError("You do not have permission to perform this action.")


    def create(self, validated_data):
        uploaded_files = validated_data.pop('uploaded_attachments', [])
        items_json_string = validated_data.pop('items')         
        try:
            items_data = json.loads(items_json_string)
        except json.JSONDecodeError:
            raise serializers.ValidationError({'items': 'Invalid JSON format.'})

        if not isinstance(items_data, list) or not items_data:
            raise serializers.ValidationError({'items': 'Items must be a non-empty list.'})

        item_serializer = ExportOperationItemSerializer(data=items_data, many=True)
        if not item_serializer.is_valid():
            raise serializers.ValidationError({'items': item_serializer.errors})
        validated_items = item_serializer.validated_data
        
        try:
            with transaction.atomic():
                user = self.context['request'].user
                export_operation = ExportOperation.objects.create(**validated_data)
                export_operation.delivere_user = user

                for item_data in validated_items:
                    ExportOperationItem.objects.create(operation=export_operation, **item_data)
            
                for file in uploaded_files:
                    OperationAttachment.objects.create(export_operation=export_operation, file=file)
                
                return export_operation
        
        except ValueError as e:
            raise serializers.ValidationError({'stock_error': str(e)})
        
        except Exception as e:
            raise serializers.ValidationError(str(e))

class ReturnSupplyItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the items within a Return Supply operation.
    Used for both creating and displaying returned items.
    """
    item_name = serializers.CharField(source='item.name', read_only=True)

    class Meta:
        model = ReturnSupplyOperationItem
        fields = ['item', 'item_name', 'returned_quantity']
        read_only_fields = ['item_name']

class ReturnSupplyOperationSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and viewing Return Supply operations.
    Accepts a nested list of 'returned_items' to be processed.
    Auto-populates related data from the original supply operation for display.
    """

    returned_items = serializers.CharField(write_only=True, required=True)
    items_details = ReturnSupplyItemSerializer(many=True, read_only=True, source='returned_items')

    recipient_user_name =serializers.CharField(source='recipient_user.name', read_only=True)

    warehouse_name = serializers.CharField(source='original_operation.warehouse.name', read_only=True)
    supplier_name = serializers.CharField(source='original_operation.supplier.name', read_only=True)
    station_name = serializers.CharField(source='original_operation.stations.name', read_only=True, allow_null=True)
    original_operation_date = serializers.DateTimeField(source='original_operation.operation_date', read_only=True)
    
    show_attachments = OperationAttachmentSerializer(many=True, read_only=True)
    uploaded_attachments = serializers.ListField(
        child=serializers.FileField(allow_empty_file=False, use_url=False),
        write_only=True,
        required=False )
        
    class Meta:
        model = ReturnSupplyOperation
        fields = [
            'id',
            'original_operation',
            'operation_date',
            'paper_ref_number',
            'returned_items',
            'items_details',
            'warehouse_name',
            'supplier_name',
            'station_name',
            'original_operation_date',
            'recipient_user',
            'recipient_user_name',
            'delivere_job_name',
            'delivere_job_number',
            'operation_statement',
            'operation_descrabtion',
            'date_response',
            'date_actual_response',
            'show_attachments', 
            'uploaded_attachments' ,
        ]

    def validate_warehouse(self, value):
        user = self.context['request'].user

        if user.is_superuser or user.user_type == 'Manager':
            return value 
        if user.user_type == 'Employee':

            if not user.managed_warehouses.filter(pk=value.pk).exists():
                raise serializers.ValidationError(
                    "You do not have permission to perform operations on this warehouse."
                )
            
            return value
        
        raise serializers.ValidationError("You do not have permission to perform this action.")


    def create(self, validated_data):
        uploaded_files = validated_data.pop('uploaded_attachments', [])
        items_json_string = validated_data.pop('returned_items')         
        try:
            items_data = json.loads(items_json_string)
        except json.JSONDecodeError:
            raise serializers.ValidationError({'items': 'Invalid JSON format.'})

        if not isinstance(items_data, list) or not items_data:
            raise serializers.ValidationError({'items': 'Items must be a non-empty list.'})


        item_serializer = ReturnSupplyItemSerializer(data=items_data, many=True)
        if not item_serializer.is_valid():
            raise serializers.ValidationError({'items': item_serializer.errors})
        validated_items = item_serializer.validated_data

        try:
            with transaction.atomic():
                user = self.context['request'].user

                print(f">>>>>>>>>>>>>{user}")
                return_operation = ReturnSupplyOperation.objects.create(**validated_data)
                return_operation.recipient_user =user
                original_operation = return_operation.original_operation

                for item_data in validated_items:
                    item_to_return = item_data['item']
                    quantity_to_return = item_data['returned_quantity']

                    try:
                        original_item_line = SupplyOperationItem.objects.select_for_update().get(
                            operation=original_operation,
                            item=item_to_return
                        )

                    except SupplyOperationItem.DoesNotExist:
                        raise serializers.ValidationError(
                            f"Item '{item_to_return.name}' was not part of the original supply operation."
                        )

                    if quantity_to_return > original_item_line.returnable_quantity:
                        raise serializers.ValidationError(
                            f"Cannot return {quantity_to_return} of '{item_to_return.name}'. "
                            f"Only {original_item_line.returnable_quantity} is available to be returned."
                        )

                    ReturnSupplyOperationItem.objects.create(
                        return_operation=return_operation,
                        **item_data
                    )

                    original_item_line.returned_quantity += quantity_to_return
                    original_item_line.save()

                for file in uploaded_files:
                    OperationAttachment.objects.create(return_supply_operation=return_operation, file=file)
                
                return return_operation
        
        except Exception as e:
            raise serializers.ValidationError(str(e))

class ReturnDispatchItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the items within a Return Export operation.
    Used for both creating and displaying returned items.
    """
    item_name = serializers.CharField(source='item.name', read_only=True)

    class Meta:
        model = ReturnDispatchOperationItem
        fields = ['item', 'item_name', 'returned_quantity']
        read_only_fields = ['item_name']

class ReturnDispatchOperationSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and viewing Return Export operations.
    Accepts a nested list of 'returned_items' to be processed.
    Auto-populates related data from the original supply operation for display.
    """

    delivere_user_name =serializers.CharField(source='recipient_user.name', read_only=True)

    returned_items = serializers.CharField(write_only=True, required=True)
    items_details = ReturnDispatchItemSerializer(many=True, read_only=True, source='returned_items')

    warehouse_name = serializers.CharField(source='original_operation.warehouse.name', read_only=True)
    beneficiary_name = serializers.CharField(source='original_operation.beneficiary.name', read_only=True)
    original_operation_date = serializers.DateTimeField(source='original_operation.operation_date', read_only=True)
    show_attachments = OperationAttachmentSerializer(many=True, read_only=True)
    uploaded_attachments = serializers.ListField(
        child=serializers.FileField(allow_empty_file=False, use_url=False),
        write_only=True,
        required=False )
    
    class Meta:
        model = ReturnDispatchOperation
        fields = [
            'id',
            'original_operation',
            'operation_date',
            'paper_ref_number',
            'returned_items',
            'items_details',
            'warehouse_name',
            'beneficiary_name',
            'original_operation_date',
            'delivere_user',
            'delivere_user_name',
            'recipient_name',
            'recipient_job_number',
            'operation_statement',
            'operation_descrabtion',
            'date_transfer',
            'date_actual_transfer',
            'show_attachments', 
            'uploaded_attachments' ,
        ]

    def validate_warehouse(self, value):
        user = self.context['request'].user

        if user.is_superuser or user.user_type == 'Manager':
            return value 
        if user.user_type == 'Employee':

            if not user.managed_warehouses.filter(pk=value.pk).exists():
                raise serializers.ValidationError(
                    "You do not have permission to perform operations on this warehouse."
                )
            
            return value
        
        raise serializers.ValidationError("You do not have permission to perform this action.")

    def create(self, validated_data):
        uploaded_files = validated_data.pop('uploaded_attachments', [])
        items_json_string = validated_data.pop('returned_items')         
        try:
            items_data = json.loads(items_json_string)
        except json.JSONDecodeError:
            raise serializers.ValidationError({'items': 'Invalid JSON format.'})

        if not isinstance(items_data, list) or not items_data:
            raise serializers.ValidationError({'items': 'Items must be a non-empty list.'})


        item_serializer = ReturnDispatchItemSerializer(data=items_data, many=True)
        if not item_serializer.is_valid():
            raise serializers.ValidationError({'items': item_serializer.errors})
        validated_items = item_serializer.validated_data
        try:
            with transaction.atomic():
                user = self.context['request'].user

                return_operation = ReturnDispatchOperation.objects.create(**validated_data)
                return_operation.delivere_user = user
                print(f"return_operation::{return_operation}")
                
                original_operation = return_operation.original_operation

                for item_data in validated_items:
                    item_to_return = item_data['item']
                    quantity_to_return = item_data['returned_quantity']

                    try:
                        original_item_line = ExportOperationItem.objects.select_for_update().get(
                            operation=original_operation,
                            item=item_to_return
                        )
                    except ExportOperationItem.DoesNotExist:
                        raise serializers.ValidationError(
                            f"Item '{item_to_return.name}' was not part of the original supply operation."
                        )


                    if quantity_to_return > original_item_line.returnable_quantity:
                        raise serializers.ValidationError(
                            f"Cannot return {quantity_to_return} of '{item_to_return.name}'. "
                            f"Only {original_item_line.returnable_quantity} is available to be returned."
                        )

                    ReturnDispatchOperationItem.objects.create(
                        return_operation=return_operation,
                        **item_data
                    )

                    original_item_line.returned_quantity += quantity_to_return
                    original_item_line.save()

                for file in uploaded_files:
                    OperationAttachment.objects.create(return_dispatch_operation=return_operation, file=file)

                return return_operation
        
        except Exception as e:
            print(e)
            raise serializers.ValidationError(str(e))

class DamagedItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the items within a Damage operation.
    Used for both creating and displaying damaged items.
    """
    item_name = serializers.CharField(source='item.name', read_only=True)

    class Meta:
        model = DamageOperationItem
        fields = ['item', 'item_name', 'quantity']
        read_only_fields = ['item_name']

class DamageOperationSerializer(serializers.ModelSerializer):

    """
    Serializer for creating and viewing Damage operations.
    Accepts a nested list of 'items' to be processed.
    Auto-populates related data from the original supply operation for display.
    """


    items = serializers.CharField(write_only=True, required=True)
    warehouse = serializers.PrimaryKeyRelatedField(
        queryset=InventoryWarehouse.active.all()
    )

    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    items_details = DamagedItemSerializer(many=True, read_only=True, source='items')
    recipient_user_name =serializers.CharField(source='recipient_user.full_name', read_only=True)

    show_attachments = OperationAttachmentSerializer(many=True, read_only=True)
    uploaded_attachments = serializers.ListField(
        child=serializers.FileField(allow_empty_file=False, use_url=False),
        write_only=True,
        required=False 
        )
    
    class Meta:
        model = DamageOperation
        fields = [
            'id',
            'warehouse',
            'warehouse_name',
            'operation_date',
            'items',
            'items_details',
            'paper_ref_number',
            'delivere_job_name',
            'delivere_job_number',
            'recipient_user',
            'recipient_user_name',
            'operation_statement',
            'operation_descrabtion',
            'reason',
            'show_attachments', 
            'uploaded_attachments' 
        ]

        extra_kwargs = {
            "reason":{'required' :True}
        }


    def validate_warehouse(self, value):
        user = self.context['request'].user

        if user.is_superuser or user.user_type == 'Manager':
            return value 
        if user.user_type == 'Employee':

            if not user.managed_warehouses.filter(pk=value.pk).exists():
                raise serializers.ValidationError(
                    "You do not have permission to perform operations on this warehouse."
                )
            return value
        
        raise serializers.ValidationError("You do not have permission to perform this action.")

    def create(self, validated_data):
        """
        Creates a DamageOperation and its related items within a single atomic transaction.
        """

        uploaded_files = validated_data.pop('uploaded_attachments', [])
        items_json_string = validated_data.pop('items')         
        try:
            items_data = json.loads(items_json_string)
        except json.JSONDecodeError:
            raise serializers.ValidationError({'items': 'Invalid JSON format.'})

        if not isinstance(items_data, list) or not items_data:
            raise serializers.ValidationError({'items': 'Items must be a non-empty list.'})


        item_serializer = DamagedItemSerializer(data=items_data, many=True)
        if not item_serializer.is_valid():
            raise serializers.ValidationError({'items': item_serializer.errors})
        validated_items = item_serializer.validated_data
        try:
            with transaction.atomic():
                user = self.context['request'].user

                damage_operation = DamageOperation.objects.create(**validated_data)
                damage_operation.recipient_user =user
                for item_data in validated_items:
                    DamageOperationItem.objects.create(operation=damage_operation, **item_data)

                for file in uploaded_files :
                    OperationAttachment.objects.create(damage_operation = damage_operation, file= file , )
                return damage_operation
        
        except ValidationError as e:
            raise e 
        
        except Exception as e:
            raise serializers.ValidationError(str(e))

class TransferOperationItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    class Meta:
        model = TransferOperationItem
        fields = ['item','item_name', 'quantity',]

class TransferOperationSerializer(serializers.ModelSerializer):
    recipient_user_name =serializers.CharField(source='recipient_user.name', read_only=True)
    items = serializers.CharField(write_only=True, required=True)
    items_details = SupplyOperationItemSerializer(many=True, read_only=True, source='items')

    from_warehouse_name = serializers.CharField(source='from_warehouse.name', read_only=True)
    to_warehouse_name = serializers.CharField(source='to_warehouse.name', read_only=True)
    show_attachments = OperationAttachmentSerializer(many=True, read_only=True)
    uploaded_attachments = serializers.ListField(
        child=serializers.FileField(max_length=100000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False 
    )

    class Meta:
        model = TransferOperation
        fields = [
            'id', 
            'from_warehouse', 
            'from_warehouse_name', 
            'to_warehouse', 
            'to_warehouse_name', 
            'operation_date',
            'items',
            'items_details',
            'paper_ref_number',
            'delivere_job_name',
            'delivere_job_number',
            'recipient_user',
            'recipient_user_name',
            'operation_statement',
            'operation_descrabtion',
            'show_attachments', 
            'uploaded_attachments' 
        ]
        extra_kwargs = {
            'items': {'required': True},
            'operation_date': {'required': True},
            'paper_ref_number': {'required': True},
            'delivere_job_name': {'required': True},
            'recipient_name': {'required': True},
        }

    def validate(self, data):
        """
        Custom validation to ensure the source and destination warehouses are not the same.
        """
        if data['from_warehouse'] == data['to_warehouse']:
            raise serializers.ValidationError("Source and destination warehouses cannot be the same.")
        return data


    def create(self, validated_data):
        """
        Creates a TransferOperation and its items, handling stock updates intelligently.
        """
        uploaded_files = validated_data.pop('uploaded_attachments', [])
        items_json_string = validated_data.pop('items')         
        try:
            items_data = json.loads(items_json_string)
        except json.JSONDecodeError:
            raise serializers.ValidationError({'items': 'Invalid JSON format.'})

        if not isinstance(items_data, list) or not items_data:
            raise serializers.ValidationError({'items': 'Items must be a non-empty list.'})


        item_serializer = TransferOperationItemSerializer(data=items_data, many=True)
        if not item_serializer.is_valid():
            raise serializers.ValidationError({'items': item_serializer.errors})
        validated_items = item_serializer.validated_data
        try:
            with transaction.atomic():

                transfer_operation = TransferOperation.objects.create(**validated_data)

                for item_data in validated_items:
                    item_instance = item_data['item']
                    quantity_to_transfer = item_data['quantity']

                    try:
                        source_stock = InventoryWarehouseitem.objects.select_for_update().get(
                            warehouse=transfer_operation.from_warehouse,
                            item=item_instance
                        )
                    except InventoryWarehouseitem.DoesNotExist:
                        raise serializers.ValidationError(
                            f"Item '{item_instance.name}' does not exist in the source warehouse."
                        )

                    if source_stock.current_quantity < quantity_to_transfer:
                        raise serializers.ValidationError(
                            f"Insufficient stock for item '{item_instance.name}' in the source warehouse. "
                            f"Required: {quantity_to_transfer}, Available: {source_stock.current_quantity}."
                        )
                    
                    source_stock.current_quantity = float(source_stock.current_quantity) - float(quantity_to_transfer)
                    source_stock.save()

                    destination_stock, created = InventoryWarehouseitem.objects.select_for_update().get_or_create(
                        warehouse=transfer_operation.to_warehouse,
                        item=item_instance,
                        defaults={'opening_balance': 0, 'unit_of_measure': source_stock.unit_of_measure}
                    )
                    
                    
                    destination_stock.current_quantity = float(destination_stock.current_quantity) + float(quantity_to_transfer)
                    destination_stock.save()

                    TransferOperationItem.objects.create(
                        operation=transfer_operation,
                        item=item_instance,
                        quantity=quantity_to_transfer
                    )

                    for file in uploaded_files: 
                        OperationAttachment.objects.create(transfer_operation=transfer_operation, file = file)

                return transfer_operation

        except Exception as e:
            raise serializers.ValidationError(str(e))

class ModifySupplyOperationSerializer(serializers.ModelSerializer):
    user_name =serializers.CharField(source='user.name', read_only=True)
    main_operations = serializers.CharField(source='original_item_line.operation.id', read_only=True)
    warehouse_name = serializers.CharField(source='original_item_line.operation.warehouse.name', read_only=True)    
    item_name = serializers.CharField(source='original_item_line.item.name', read_only=True)    
    class Meta:
        model = ModifySupplyOperation
        fields = ['id','original_item_line','item_name','warehouse_name','main_operations','user','user_name', 'reason','operation_date','old_quantity', 'new_quantity']

    def validate(self, data):
        original_item = data['original_item_line']
        current_effective_quantity = original_item.effective_quantity
        data['old_quantity'] = current_effective_quantity
        return data

class ModifyExportOperationSerializer(serializers.ModelSerializer):
    user_name =serializers.CharField(source='user.name', read_only=True)
    warehouse_name = serializers.CharField(source='original_item_line.operation.warehouse.name', read_only=True)    
    main_operations = serializers.CharField(source='original_item_line.operation.id', read_only=True)
    item_name = serializers.CharField(source='original_item_line.item.name', read_only=True)    
    class Meta:
        model = ModifyExportOperation
        fields = ['id','original_item_line','item_name','warehouse_name','main_operations','user','user_name', 'reason','operation_date','old_quantity', 'new_quantity']

    def validate(self, data):
        original_item = data['original_item_line']
        current_effective_quantity = original_item.effective_quantity
        data['old_quantity'] = current_effective_quantity
        
        return data