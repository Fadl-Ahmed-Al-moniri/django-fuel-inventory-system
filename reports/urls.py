# apps/reports/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('general-warehouse/', views.GeneralWarehouseReportView.as_view(), name='report-general-warehouse'),
    path('warehouse-status/', views.WarehouseStatusReportView.as_view(), name='report-warehouse-status'),
    path('supplier-operations/', views.SupplierOperationsReportView.as_view(), name='report-supplier-operations'),
    path('beneficiary-operations/', views.BeneficiaryOperationsReportView.as_view(), name='report-beneficiary-operations'),
    path('stations-operations/', views.StationsOperationsReportView.as_view(), name='report-stations-operations'),
    path('item-status/', views.ItemStatusReportView.as_view(), name='report-stations-operations'),
    path('general-item/', views.GeneralItemOperationsReportView.as_view(), name='report-stations-operations'),
]
