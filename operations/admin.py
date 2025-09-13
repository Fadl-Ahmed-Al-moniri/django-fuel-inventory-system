from django.contrib import admin
from django.contrib import admin
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe


from .models import (ModifyExportOperation, ModifySupplyOperation, SupplyOperation, SupplyOperationItem,
                    ExportOperation, ExportOperationItem,OperationAttachment)

from .models import (   DamageOperation, DamageOperationItem, 
                        ExportOperation, ExportOperationItem,
                        SupplyOperation , SupplyOperationItem  ,
                        ReturnDispatchOperation ,ReturnDispatchOperationItem,
                        ReturnSupplyOperation,ReturnSupplyOperationItem,
                        TransferOperation, TransferOperationItem)

class SupplyOperationItemInline(admin.TabularInline):

    model = SupplyOperationItem
    extra = 1  

class ExportOperationItemInline(admin.TabularInline):

    model = ExportOperationItem
    extra = 1
    search_fields = ['id']
    
class ReturnSupplyOperationItemInline(admin.TabularInline):

    model = ReturnSupplyOperationItem
    extra = 1
    search_fields = ['id']
    
class ReturnDispatchOperationItemInline(admin.TabularInline):

    model = ReturnDispatchOperationItem
    extra = 1
    search_fields = ['id']
    
@admin.register(SupplyOperation)
class SupplyOperationAdmin(admin.ModelAdmin):

    inlines = [SupplyOperationItemInline]
    list_display = ('id', 'warehouse', 'supplier', 'operation_date', 'display_items_and_quantities')
    list_filter = ('operation_date', 'warehouse', 'supplier')
    search_fields = ('id', 'warehouse__name', 'supplier__name')

    def display_items_and_quantities(self, obj):

        items = obj.items.all()
        if not items:
            return "no items"
        
        item_list = format_html_join(
            mark_safe('  '), 
            '<li>{} (quantity: {})</li>',
            ((item.item.name, item.quantity) for item in items) 
        )
        return mark_safe(f"<ul>{item_list}</ul>")

    display_items_and_quantities.short_description = "items and quantity"

@admin.register(ExportOperation)
class ExportOperationAdmin(admin.ModelAdmin):


    inlines = [ExportOperationItemInline]
    list_display = ('id', 'warehouse', 'beneficiary', 'operation_date', 'display_items_and_quantities')
    list_filter = ('operation_date', 'warehouse', 'beneficiary')
    search_fields = ('id', 'warehouse__name', 'beneficiary__name')

    def display_items_and_quantities(self, obj):
        items = obj.items.all() 
        if not items:
            return "no items"
        
        item_list = format_html_join(
            mark_safe('  '), 
            '<li>{} (quantity: {})</li>',
            ((item.item.name, item.quantity) for item in items) 
        )
        return mark_safe(f"<ul>{item_list}</ul>")

    display_items_and_quantities.short_description = "items and quantity"

@admin.register(ReturnSupplyOperation)
class ReturnSupplyOperationAdmin(admin.ModelAdmin):

    inlines = [ReturnSupplyOperationItemInline]
    list_display = ('id', 'original_operation', 'operation_date',)
    list_filter = ('id', 'original_operation', 'operation_date')
    search_fields = ('id',)

@admin.register(ReturnDispatchOperation)
class ReturnDispatchOperationAdmin(admin.ModelAdmin):

    inlines = [ReturnDispatchOperationItemInline]
    list_display = ('id', 'original_operation', 'operation_date',)
    list_filter = ('id', 'original_operation', 'operation_date')
    search_fields = ('id',)

@admin.register(SupplyOperationItem)
class SupplyOperationItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'operation', 'item', 'quantity','returned_quantity','effective_quantity')
    list_select_related = ('operation', 'item', 'operation__warehouse') 
    search_fields = ('item__name', 'operation__id')

@admin.register(ExportOperationItem)
class ExportOperationItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'operation', 'item', 'quantity','returned_quantity','effective_quantity')
    list_select_related = ('operation', 'item', 'operation__warehouse')
    search_fields = ('item__name', 'operation__id')

@admin.register(ReturnSupplyOperationItem)
class ReturnSupplyOperationItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'return_operation', 'item', 'returned_quantity')
    list_select_related = ('return_operation', 'item', 'operation__warehouse')
    search_fields = ('return_operation', 'item')

@admin.register(ReturnDispatchOperationItem)
class ReturnDispatchOperationItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'return_operation', 'item', 'returned_quantity')
    list_select_related = ('return_operation', 'item',)
    search_fields = ('return_operation', 'item')

    
@admin.register(ModifySupplyOperation)
class ModifySupplyOperationAdmin(admin.ModelAdmin):
    list_display = ('id', 'original_item_line', 'operation_date', 'old_quantity','new_quantity','difference')
    list_select_related = ('original_item_line', )
    search_fields = ('original_item_line', 'operation_date')

    
@admin.register(ModifyExportOperation)
class ModifyExportOperationAdmin(admin.ModelAdmin):
    list_display = ('id', 'original_item_line','user', 'operation_date', 'old_quantity','new_quantity','difference')
    list_select_related = ('original_item_line', )
    search_fields = ('original_item_line', 'operation_date')


admin.site.register(DamageOperationItem ,)
admin.site.register(DamageOperation ,)
admin.site.register(TransferOperationItem ,)
admin.site.register(OperationAttachment ,)
admin.site.register(TransferOperation,)
