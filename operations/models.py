from datetime import datetime
import os
from django.conf import settings
from django.db import models
from marshmallow import ValidationError
from inventory.models import InventoryWarehouseitem , Item ,Stations , InventoryWarehouse
from accounts.models import User , Supplier  , Beneficiary
from django.utils.translation import gettext_lazy as _


class SupplyOperation(models.Model):
    warehouse = models.ForeignKey(InventoryWarehouse ,on_delete=models.PROTECT, related_name = 'warehouse_main_operations' )
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT , related_name= "reletions_to_supplier_model")
    stations = models.ForeignKey(Stations, on_delete=models.PROTECT , related_name= "reletions_to_stations_model",)
    operation_date =  models.DateTimeField()
    paper_ref_number = models.DecimalField(max_digits=20, decimal_places=0, default=0 ,help_text="Reference Paper Number")
    supply_bon_number = models.DecimalField(max_digits=20, decimal_places=0, default=0 ,help_text="Supply Bond Number")
    delivere_job_name = models.CharField(max_length=255,help_text="Delivere Name " , )
    delivere_job_number = models.DecimalField(max_digits=20, decimal_places=0, default=0 ,help_text="Delivere Job Number ")
    recipient_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='received_supplies',
        null=True,

        verbose_name=_("Internal Recipient (if applicable)"),
        help_text=_("If the recipient is a registered user, select them here.")
    )
    operation_statement = models.TextField( max_length=255,blank=True)
    operation_descrabtion = models.TextField( max_length=255,blank=True)

    def __str__(self):
        return f"{self.warehouse.name} -supplier : {self.supplier} - {self.operation_date}"

class SupplyOperationItem(models.Model):

    operation = models.ForeignKey(SupplyOperation, related_name='items', on_delete=models.PROTECT)
    item = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name=_("item"))
    quantity = models.DecimalField(_("quantity"), max_digits=15, decimal_places=2 ,)
    returned_quantity = models.DecimalField(
        _("Returned Quantity"), 
        max_digits=15, 
        decimal_places=2, 
        default=0.00,
        help_text="Total quantity of this item returned against this dispatch line."
    )

    @property
    def returnable_quantity(self):
        """Calculates the remaining quantity that can be returned."""
        return self.quantity - self.returned_quantity


    def __str__(self):
        return f"{self.operation }in {self.operation.warehouse.name} with item {self.item.name} quantity= {self.quantity}"
    
    @property
    def effective_quantity(self):
        """
        Returns the most up-to-date quantity after all modifications.
        """
        last_modification = self.modifications.order_by('-operation_date').first()
        if last_modification:
            return last_modification.new_quantity
        return self.quantity

    class Meta:
        unique_together = ('operation', 'item')

class ExportOperation(models.Model):
    warehouse = models.ForeignKey(InventoryWarehouse ,on_delete=models.PROTECT, related_name = 'warehouse_export_operations' )
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.PROTECT , related_name= "reletions_to_beneficiary_model")
    operation_date =  models.DateTimeField()
    paper_ref_number = models.DecimalField(max_digits=20, decimal_places=0, default=0 ,help_text="Reference Paper Number")
    delivere_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='received_export',
        null=True,

        verbose_name=_("Internal delivere (if applicable)"),
        help_text=_("If the delivere is a registered user, select them here.")
    )
    
    recipient_name = models.CharField(max_length=255,help_text="Recipient name" , )
    recipient_job_number = models.CharField(max_length=255,help_text="Recipient Job Number" , )
    date_transfer = models.DateTimeField( )
    date_actual_transfer = models.DateTimeField()
    operation_statement = models.TextField( max_length=255,blank=True)
    operation_descrabtion = models.TextField( max_length=255,blank=True)

    def __str__(self):
        return f"{self.warehouse.name} -beneficiary : {self.beneficiary} - {self.operation_date}"

class ExportOperationItem(models.Model):

    operation = models.ForeignKey(ExportOperation, related_name='items', on_delete=models.PROTECT)
    item = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name=_("item"))
    quantity = models.DecimalField(_("quantity"), max_digits=15, decimal_places=2 ,)

    returned_quantity = models.DecimalField(
        _("Returned Quantity"), 
        max_digits=15, 
        decimal_places=2, 
        default=0.00,
        help_text="Total quantity of this item returned against this dispatch line."
    )

    @property
    def returnable_quantity(self):
        """Calculates the remaining quantity that can be returned."""
        return self.quantity - self.returned_quantity

    @property
    def effective_quantity(self):
        """
        Returns the most up-to-date quantity after all modifications.
        """
        last_modification = self.modifications.order_by('-operation_date').first()
        if last_modification:
            return last_modification.new_quantity
        return self.quantity
    class Meta:
        unique_together = ('operation', 'item')




    def __str__(self):
        return f"{self.operation }in {self.operation.warehouse.name} with item {self.item.name} quantity= {self.quantity}"
    
class ReturnSupplyOperation(models.Model):
    """
    Header for a return operation against an original supply.
    This links the return to the original transaction.
    """
    original_operation = models.ForeignKey(
        SupplyOperation, 
        on_delete=models.PROTECT, 
        related_name="returns",
        verbose_name=_("Original Supply Operation")
    )
    operation_date = models.DateTimeField(_("Return Date"))
    paper_ref_number = models.CharField(_("Paper Reference Number"), max_length=100, blank=True)
    delivere_job_name = models.CharField(max_length=255,help_text="Delivere Name " , )
    delivere_job_number = models.DecimalField(max_digits=20, decimal_places=0, default=0 ,help_text="Delivere Job Number ")
    recipient_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='received_return_supplies',
        null=True,

        verbose_name=_("Internal Recipient (if applicable)"),
        help_text=_("If the recipient is a registered user, select them here.")
    )

    operation_statement = models.TextField( max_length=255,blank=True)
    operation_descrabtion = models.TextField( max_length=255,blank=True)
    date_response = models.DateTimeField()
    date_actual_response = models.DateTimeField()

    class Meta:
        verbose_name = _("Return Supply Operation")
        verbose_name_plural = _("Return Supply Operations")

    def __str__(self):
        return f"Return against Supply #{self.original_operation.id}"

class ReturnSupplyOperationItem(models.Model):
    """
    A specific item and quantity being returned against a supply operation.
    This is where the actual returned quantity is stored.
    """
    return_operation = models.ForeignKey(ReturnSupplyOperation, related_name='returned_items', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name=_("Item"))
    returned_quantity = models.DecimalField(_("Returned Quantity"), max_digits=15, decimal_places=2)


    class Meta:
        unique_together = ('return_operation', 'item')

class ReturnDispatchOperation(models.Model):
    """Header for a return operation against an original dispatch."""
    original_operation = models.ForeignKey(
        ExportOperation, 
        on_delete=models.PROTECT, 
        related_name="returns",
        verbose_name=_("Original Dispatch Operation")
    )
    operation_date = models.DateTimeField(_("Return Date"))
    paper_ref_number = models.CharField(_("Paper Reference Number"), max_length=100, blank=True)
    delivere_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='received_return_dispatch',
        null=True,

        verbose_name=_("Internal delivere (if applicable)"),
        help_text=_("If the delivere is a registered user, select them here.")
    )
    
    recipient_name = models.CharField(max_length=255,help_text="Recipient name" , )
    recipient_job_number = models.CharField(max_length=255,help_text="Recipient Job Number" , )
    date_transfer = models.DateTimeField( )
    date_actual_transfer = models.DateTimeField()
    operation_statement = models.TextField( max_length=255,blank=True)
    operation_descrabtion = models.TextField( max_length=255,blank=True)

    class Meta:
        verbose_name = _("Return Dispatch Operation")
        verbose_name_plural = _("Return Dispatch Operations")

    def __str__(self):
        return f"Return against Dispatch #{self.original_operation.beneficiary}"

class ReturnDispatchOperationItem(models.Model):
    """A specific item and quantity being returned against a dispatch operation."""
    return_operation = models.ForeignKey(ReturnDispatchOperation, related_name='returned_items', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name=_("Item"))
    returned_quantity = models.DecimalField(_("Returned Quantity"), max_digits=15, decimal_places=2)


    class Meta:
        unique_together = ('return_operation', 'item')

class DamageOperation(models.Model):
    warehouse = models.ForeignKey(InventoryWarehouse ,on_delete=models.PROTECT, related_name = 'warehouse_damage_operations' )
    operation_date =  models.DateTimeField()
    paper_ref_number = models.DecimalField(max_digits=20, decimal_places=0, default=0 ,help_text="Reference Paper Number")
    delivere_job_name = models.CharField(max_length=255,help_text="Delivere Name " , )
    delivere_job_number = models.DecimalField(max_digits=20, decimal_places=0, default=0 ,help_text="Delivere Job Number ")
    recipient_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='received_damage',
        null=True,

        
        verbose_name=_("Internal Recipient (if applicable)"),
        help_text=_("If the recipient is a registered user, select them here.")
    )    
    operation_statement = models.TextField( max_length=255,blank=True)
    operation_descrabtion = models.TextField( max_length=255,blank=True)
    reason = models.TextField( max_length=255,blank=True)


    def __str__(self):
        return f"{self.warehouse.name} - {self.operation_date}"

class DamageOperationItem(models.Model):
    operation = models.ForeignKey(DamageOperation, related_name='items', on_delete=models.PROTECT)
    item = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name=_("item"))
    quantity = models.DecimalField(_("quantity"), max_digits=15, decimal_places=2 ,)
    class Meta:
        unique_together = ('operation', 'item')

    
    def __str__(self):
        return f"{self.item.name} - {self.quantity} in operation {self.operation.id}"

class TransferOperation(models.Model):
    from_warehouse = models.ForeignKey(InventoryWarehouse ,on_delete=models.PROTECT, related_name = 'warehouse_transfer_from_operations' )
    to_warehouse = models.ForeignKey(InventoryWarehouse ,on_delete=models.PROTECT, related_name = 'warehouse_transfer_to_operations' )
    operation_date =  models.DateTimeField()
    paper_ref_number = models.DecimalField(max_digits=20, decimal_places=0, default=0 ,help_text="Reference Paper Number")
    delivere_job_name = models.CharField(max_length=255,help_text="Delivere Name " , )
    delivere_job_number = models.DecimalField(max_digits=20, decimal_places=0, default=0 ,help_text="Delivere Job Number ")
    recipient_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='received_transfer',
        verbose_name=_("Internal Recipient (if applicable)"),
        help_text=_("If the recipient is a registered user, select them here.")
    )   
    
    operation_statement = models.TextField( max_length=255,blank=True)
    operation_descrabtion = models.TextField( max_length=255,blank=True)
    reason = models.TextField( max_length=255,blank=True)


    def __str__(self):
        return f"from :{self.from_warehouse.name} to:{self.to_warehouse.name} - {self.operation_date}  "

class TransferOperationItem(models.Model): 
    operation = models.ForeignKey(TransferOperation, related_name='items', on_delete=models.PROTECT)
    item = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name=_("item"))
    quantity = models.DecimalField(_("quantity"), max_digits=15, decimal_places=2 ,)
    
    def __str__(self):
        return f"{self.item.name} - {self.quantity} in operation {self.operation.id}"
    
    class Meta:
        unique_together = ('operation', 'item')

class OperationAttachment(models.Model):

    def operation_attachment_path(instance, filename):
        if instance.supply_operation_id:
            operation_type = "supply"
        elif instance.export_operation_id:
            operation_type = "export"
        elif instance.return_supply_operation_id:
            operation_type = "return_supply"
        elif instance.return_dispatch_operation_id:
            operation_type = "return_dispatch"
        elif instance.damage_operation_id:
            operation_type = "damage"
        elif instance.transfer_operation_id:
            operation_type = "transfer"
        else:
            operation_type = "unknown"
        today = datetime.now().strftime("%Y/%m/%d")

        return os.path.join("operation_attachments", operation_type, today, filename)

    supply_operation = models.ForeignKey(SupplyOperation, on_delete=models.CASCADE, related_name='attachments', null=True, blank=True)
    export_operation = models.ForeignKey(ExportOperation, on_delete=models.CASCADE, related_name='attachments', null=True, blank=True)
    return_supply_operation = models.ForeignKey(ReturnSupplyOperation, on_delete=models.CASCADE, related_name='attachments', null=True, blank=True)
    return_dispatch_operation = models.ForeignKey(ReturnDispatchOperation, on_delete=models.CASCADE, related_name='attachments', null=True, blank=True)
    damage_operation = models.ForeignKey(DamageOperation, on_delete=models.CASCADE, related_name='attachments', null=True, blank=True)
    transfer_operation = models.ForeignKey(TransferOperation, on_delete=models.CASCADE, related_name='attachments', null=True, blank=True)

    file = models.FileField(
        _("File"),
        upload_to=operation_attachment_path
    )
    description = models.CharField(_("Description"), max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Attachment for operation {self.supply_operation_id or self.export_operation_id}"
    
    class Meta:
        verbose_name = _("Operation Attachment")
        verbose_name_plural = _("Operation Attachments")

class ModifySupplyOperation(models.Model):
    original_item_line = models.ForeignKey(
        SupplyOperationItem, 
        on_delete=models.PROTECT,
        related_name='modifications'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,

        related_name='received_modify_supplies',
        verbose_name=_("Internal delivere (if applicable)"),
        help_text=_("If the delivere is a registered user, select them here.")
    )
    operation_date = models.DateTimeField()
    reason = models.TextField()
    old_quantity = models.DecimalField(max_digits=15, decimal_places=2)
    new_quantity = models.DecimalField(max_digits=15, decimal_places=2)

    @property
    def difference(self):
        return self.new_quantity - self.old_quantity

class ModifyExportOperation(models.Model):
    original_item_line = models.ForeignKey(
        ExportOperationItem, 
        on_delete=models.PROTECT,
        related_name='modifications'
    )

    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,

        related_name='received_modify_export',
        verbose_name=_("Internal delivere (if applicable)"),
        help_text=_("If the delivere is a registered user, select them here.")
    )
    operation_date = models.DateTimeField()
    reason = models.TextField()
    old_quantity = models.DecimalField(max_digits=15, decimal_places=2)
    new_quantity = models.DecimalField(max_digits=15, decimal_places=2)

    @property
    def difference(self):
        return self.new_quantity - self.old_quantity
