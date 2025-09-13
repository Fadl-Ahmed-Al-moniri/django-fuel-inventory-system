from django.urls import path, include
from rest_framework.routers import DefaultRouter
from inventory import views 

router = DefaultRouter()

router.register(r'warehouse', views.WarehouseViewSet, basename='warehouses')
router.register(r'warehouse-item', views.WarehouseItemViewSet, basename='warehouse-item')
router.register(r'item', views.ItemViewSet, basename='items')
router.register(r'station', views.StationViewSet, basename='stations')

urlpatterns = [
    path('api/inventory/', include(router.urls)),
]
