from django.contrib import admin
from .models import Item, InventoryWarehouse, InventoryWarehouseitem, Stations




class CustomInventoryWarehouseitem(admin.ModelAdmin):
    list_display = ['id','item_name', 'warehouse_name', 'current_quantity', 'unit_of_measure', 'last_updated']
    search_fields = ['item__name', 'warehouse__name']
    def item_name(self,obj):
        if obj:
            return obj.item.name
        return 'null-name'
    
    def warehouse_name(self,obj):
        if obj:
            return obj.warehouse.name
        return 'null-name'
    

class CustomInventoryWarehouse(admin.ModelAdmin):
    list_display = ['id','name', 'calssification', 'storekeeper', 'phone_warehouse']
    search_fields=  ['name', 'storekeeper']


admin.site.register(Item)
admin.site.register(InventoryWarehouse , CustomInventoryWarehouse)
admin.site.register(InventoryWarehouseitem, CustomInventoryWarehouseitem) 
admin.site.register(Stations)
