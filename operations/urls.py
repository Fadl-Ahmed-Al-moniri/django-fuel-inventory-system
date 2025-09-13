from django.urls import path, include
from rest_framework.routers import DefaultRouter
from operations import views 

router = DefaultRouter()

router.register(r'supply', views.SupplyOperationViewSet, basename='supplys')
router.register(r'modify_supply', views.ModifySupplyOperationViewSet, basename='modify_supply')
router.register(r'export', views.ExportOperationViewSet, basename='exports')
router.register(r'modify_export', views.ModifyExportOperationViewSet, basename='modify_exports')
router.register(r'return_supply', views.ReturnSupplyOperationViewSet, basename='return_supplys')
router.register(r'return_export', views.ReturnDispatchOperationViewSet, basename='return_exports')
router.register(r'damage', views.DamageOperationViewSet, basename='damages')
router.register(r'transfer', views.TransferOperationViewSet, basename='transfers')

urlpatterns = [
    path('api/operations/', include(router.urls)),
]
