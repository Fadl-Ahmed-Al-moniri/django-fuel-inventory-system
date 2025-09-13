
from decimal import Decimal
from django.db import transaction
from django.db.models.signals import post_save, post_delete , pre_migrate
from django.dispatch import receiver

from .models import (
    DamageOperationItem,
    ModifyExportOperation,
    ModifySupplyOperation,
    SupplyOperationItem, 
    ExportOperationItem,
    ReturnSupplyOperationItem, 
    ReturnDispatchOperationItem,
    TransferOperationItem 
)
from inventory.models import InventoryWarehouseitem


@receiver(post_save, sender=SupplyOperationItem)
def add_stock_on_supply(sender, instance, created, **kwargs):
    """
    Signal to INCREASE stock quantity after a SupplyOperationItem is created.
    """
    try:
        if created:
                with transaction.atomic():
                    stock, _ = InventoryWarehouseitem.objects.get_or_create(
                        warehouse=instance.operation.warehouse,
                        item=instance.item
                    ) 
                    stock.current_quantity = float(stock.current_quantity) + float(instance.quantity)
                    stock.save()
    except Exception as e :
        raise e
    


@receiver(post_delete, sender=SupplyOperationItem)
def remove_stock_on_supply_delete(sender, instance, **kwargs):
    """
    Signal to DECREASE stock quantity if a SupplyOperationItem is deleted.
    (This corrects the stock if an operation is undone).
    """
    try :
        with transaction.atomic():
            stock = InventoryWarehouseitem.objects.get(
                warehouse=instance.operation.warehouse,
                item=instance.item
            )
            stock.current_quantity = float(stock.current_quantity) - float(instance.quantity)
            stock.save()
    except Exception as e :
        raise e

@receiver(post_save, sender=ExportOperationItem)
def remove_stock_on_dispatch(sender, instance, created, **kwargs):
    """
    Signal to DECREASE stock quantity after an ExportOperationItem is created.
    """
    if created:
        with transaction.atomic():
            stock, _ = InventoryWarehouseitem.objects.get_or_create(
                warehouse=instance.operation.warehouse,
                item=instance.item
            )
            if stock.current_quantity < instance.quantity:
                raise ValueError(f"Insufficient stock for item '{instance.item.name}'. Cannot export.")
            
            stock.current_quantity = float(stock.current_quantity) - float(instance.quantity)
            stock.save()

@receiver(post_delete, sender=ExportOperationItem)
def add_stock_on_dispatch_delete(sender, instance, **kwargs):
    """
    Signal to INCREASE stock quantity if an ExportOperationItem is deleted.
    (This corrects the stock if an operation is undone).
    """
    with transaction.atomic():
        stock = InventoryWarehouseitem.objects.get(
            warehouse=instance.operation.warehouse,
            item=instance.item
        )
        stock.current_quantity = float(stock.current_quantity) - float(instance.quantity)
        stock.save()


@receiver(post_save, sender=ReturnSupplyOperationItem)
def remove_stock_on_return_supply(sender, instance, created, **kwargs):
    """
    Signal to DECREASE stock quantity after a ReturnSupplyOperationItem is created.
    (Goods are returned TO the supplier, so they leave our warehouse).
    """
    if created:
        with transaction.atomic():
            warehouse = instance.return_operation.original_operation.warehouse
            stock = InventoryWarehouseitem.objects.get(
                warehouse=warehouse,
                item=instance.item
            )
            
            if stock.current_quantity < instance.returned_quantity:
                raise ValueError(f"Insufficient stock for item '{instance.item.name}' to return.")

            stock.current_quantity = float(stock.current_quantity) - float(instance.returned_quantity)
            stock.save()

@receiver(post_delete, sender=ReturnSupplyOperationItem)
def add_stock_on_return_supply_delete(sender, instance, **kwargs):
    """
    Signal to INCREASE stock quantity if a ReturnSupplyOperationItem is deleted.
    (Undoes the return).
    """
    with transaction.atomic():
        warehouse = instance.return_operation.original_operation.warehouse
        stock = InventoryWarehouseitem.objects.get(
            warehouse=warehouse,
            item=instance.item
        )
        stock.current_quantity = float(stock.current_quantity) + float(instance.returned_quantity)
        stock.save()


@receiver(post_save, sender=ReturnDispatchOperationItem)
def add_stock_on_return_dispatch(sender, instance, created, **kwargs):
    """
    Signal to INCREASE stock quantity after a ReturnDispatchOperationItem is created.
    (Goods are returned FROM the beneficiary, so they come back to our warehouse).
    """
    if created:
        with transaction.atomic():
            warehouse = instance.return_operation.original_operation.warehouse
            stock, _ = InventoryWarehouseitem.objects.get_or_create(
                warehouse=warehouse,
                item=instance.item
            )
            stock.current_quantity = float(stock.current_quantity) + float(instance.returned_quantity)
            stock.save()

@receiver(post_delete, sender=ReturnDispatchOperationItem)
def remove_stock_on_return_dispatch_delete(sender, instance, **kwargs):
    """
    Signal to DECREASE stock quantity if a ReturnDispatchOperationItem is deleted.
    (Undoes the return).
    """
    with transaction.atomic():
        warehouse = instance.return_operation.original_operation.warehouse
        stock = InventoryWarehouseitem.objects.get(
            warehouse=warehouse,
            item=instance.item
        )
        stock.current_quantity = float(stock.current_quantity) - float(instance.returned_quantity)
        stock.save()


@receiver(post_save, sender=DamageOperationItem)
def remove_stock_on_damage(sender, instance, **kwargs):
    """
    Signal to DECREASE stock quantity if a item is damage.
    (This corrects the stock if an operation is undone).
    """
    with transaction.atomic():
        stock = InventoryWarehouseitem.objects.get(
            warehouse=instance.operation.warehouse,
            item=instance.item
        )
        if stock.current_quantity < instance.quantity:
            raise ValueError(f"Insufficient stock for item '{instance.item.name}' to mark as damaged.")
        stock.current_quantity = float(stock.current_quantity) - float(instance.quantity)
        stock.save()





@receiver(post_save, sender=ModifySupplyOperation)
def update_stock_on_supply_modification(sender, instance, created, **kwargs):
    if created:

        try: 
            with transaction.atomic() :
                warehouse = instance.original_item_line.operation.warehouse
                item = instance.original_item_line.item
                
                stock, _ = InventoryWarehouseitem.objects.get_or_create(
                    warehouse=warehouse,
                    item=item
                )
                if stock.current_quantity < instance.new_quantity:
                    raise ValueError(f"Insufficient stock for item '{instance.original_item_line.item.name}' to return.")

                stock.current_quantity = float(stock.current_quantity) + float(instance.difference)
                stock.save()
        except Exception as e:
            raise e
@receiver(post_save, sender=ModifyExportOperation)
def update_stock_on_export_modification(sender, instance, created, **kwargs):
    if created:
        try: 
            with transaction.atomic() :
                warehouse = instance.original_item_line.operation.warehouse
                item = instance.original_item_line.item
                
                stock, _ = InventoryWarehouseitem.objects.get_or_create(
                    warehouse=warehouse,
                    item=item
                )
                if stock.current_quantity < instance.new_quantity:
                    raise ValueError(f"Insufficient stock for item '{instance.original_item_line.item.name}' to return.")

                stock.current_quantity = float(stock.current_quantity) + float(instance.difference)
                stock.save()
        except Exception as e:
            raise e