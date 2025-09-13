# في apps/core/mixins.py

class UserPermissionsMixin:
    """
    Mixin to filter querysets based on a hierarchical permission model.
    - Managers see everything.
    - Employees see data for warehouses they are directly responsible for.
    """
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if not user.is_authenticated:
            return queryset.none()

        if user.is_superuser or user.user_type == 'Manager':
            return queryset


        if user.user_type == 'Employee':
            managed_warehouses_qs = user.managed_warehouses.all()
            
            if not managed_warehouses_qs.exists():
                return queryset.none()

            # اسم حقل البحث عن المخزن (نفس الطريقة السابقة)
            warehouse_field_lookup = getattr(self, 'warehouse_field_lookup', 'warehouse__in')
            
            return queryset.filter(**{warehouse_field_lookup: managed_warehouses_qs})
            
        # كإجراء أمني، لا تعرض أي شيء للحالات الأخرى
        return queryset.none()
