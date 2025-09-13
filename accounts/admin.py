from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User , Beneficiary , Supplier 


class CustomUserAdmin(UserAdmin):

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('user_type', 'first_name', 'last_name','manager'), }),
    )
    fieldsets = UserAdmin.fieldsets + (
        ('User Role', {'fields': ('user_type',)}),
    )

    search_fields = ('username', 'first_name', 'last_name', 'email')
    list_display = ('pk', 'username', 'email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')



class CustomBeneficiary(admin.ModelAdmin):
        
    fields = ["name", "phone_number",'is_active']


class CustomSupplier(admin.ModelAdmin):

    fields = [ "name", "phone_number",'is_active']

admin.site.register(User, CustomUserAdmin)
admin.site.register(Beneficiary, CustomBeneficiary)
admin.site.register(Supplier, CustomSupplier)
