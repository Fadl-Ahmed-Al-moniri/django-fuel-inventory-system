from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.services.managers import ActiveManager


class Item(models.Model):

        
    name = models.CharField(max_length=255, unique=True)

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active"),
        help_text=_("Uncheck this to 'freeze' or 'soft delete' the item. It will not be available for new operations.")
    )
    objects = models.Manager() 
    active = ActiveManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Inventory Item")
        verbose_name_plural = _("Inventory Items")
        ordering = ['name']




class InventoryWarehouse(models.Model):
    """
    Model representing a warehouse for fuel inventory.
    """
    name = models.CharField(max_length=255, unique=True)
    calssification = models.CharField(max_length=255 , blank=True,)
    storekeeper = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_warehouses',
        verbose_name=_("Storekeeper"),
        help_text=_("The user responsible for this warehouse."),
    )

    phone_warehouse = models.CharField(max_length=20, )
    parent = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='children', 
        verbose_name=_("Parent Warehouse")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active"),
        help_text=_("Uncheck this to 'freeze' or 'soft delete' the item. It will not be available for new operations.")
    )
    objects = models.Manager() 
    active = ActiveManager()


    def __str__(self):
        return self.name

    class Meta:
        verbose_name =_("Fuel Inventory Warehouse")
        verbose_name_plural = _("Fuel Inventory Warehouses")
        ordering = ['name']



class InventoryWarehouseitem(models.Model):
    """
    Model representing an item in the fuel inventory warehouse.
    """
    
    class UnitofMeasure(models.TextChoices):
        """
        Choices for unit of measure for inventory items.
        """
        LITERS = 'Liters' , _('Liters')
        BARREL = 'Barrel' , _('Barrel')
        GALLON = 'Gallon' , _('Gallon')
        UNITS = 'Units' , _('Units')



    warehouse = models.ForeignKey(InventoryWarehouse, on_delete=models.PROTECT, related_name='warehouse')
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='warehouse_items')
    opening_balance = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    current_quantity = models.DecimalField(max_digits=20, decimal_places=2, default=0.00, )
    last_updated = models.DateTimeField(auto_now=True)
    unit_of_measure = models.CharField(max_length=50, choices= UnitofMeasure.choices, default=UnitofMeasure.LITERS)

    def __str__(self):
        return f"{self.item.name} in {self.warehouse.name}"
    

    def operation(self, operation_type ,value):
        """
            This function to do some operation on current_quantity.
            
            Parameters:
            - operation_type the process only sum or sub.
            - value the value rect on current_quantity.
        """
        if operation_type =="sum":
            self.current_quantity += value
        if operation_type =="sub":
            self.current_quantity -= value


        else :
            return SyntaxError()
        
        self.save()


    def check_type(self, obj):
        if self.item.name ==obj.item.name:
            return True
        else :
            False

    class Meta:
        verbose_name = _("Inventory Warehouse Item")
        verbose_name_plural = _("Inventory Warehouse Items")
        ordering = ['warehouse', 'item']




class Stations(models.Model):
    """
    Model representing a fuel station.
    """
    name = models.CharField(max_length=255, unique=True)
    location = models.CharField(max_length=255)
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active"),
        help_text=_("Uncheck this to 'freeze' or 'soft delete' the item. It will not be available for new operations.")
    )
    objects = models.Manager() 
    active = ActiveManager()


    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Fuel Station")
        verbose_name_plural = _("Fuel Stations")
        ordering = ['name']