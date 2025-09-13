from rest_framework.response import Response
from rest_framework import status 
from .serializers import  GeneralItemReportSerializer,  GeneralWarehouseReportSerializer
from .renderers import ExcelRenderer , PdfRenderer
from rest_framework.renderers import JSONRenderer  
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from .serializers import (
    GeneralWarehouseReportSerializer, WarehouseItemStatusSerializer,
    ReportSupplySerializer, ReportExportSerializer
)
from operations.models import  ReturnDispatchOperation,DamageOperation,  SupplyOperation, ExportOperation, ReturnSupplyOperation, TransferOperation
from inventory.models import InventoryWarehouseitem
from core.services.mixins import UserPermissionsMixin


class ReportAPIView(APIView):
    """
    Basic API interface for reports with support for exporting and date search.
    """
    renderer_classes = [JSONRenderer, ExcelRenderer, PdfRenderer]

    def get_date_filters(self):
        """The date filters are extracted from the request."""
        start_date_str = self.request.query_params.get('start_date')
        end_date_str = self.request.query_params.get('end_date')
        filters = {}
        if start_date_str:
            filters['start_date'] = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        if end_date_str:
            filters['end_date'] = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        return filters

    def add_date_filters(self, queryset, date_field_name, date_filters):
        """Date filters are applied to the QuerySet."""
        if 'start_date' in date_filters:
            queryset = queryset.filter(**{f'{date_field_name}__gte': date_filters['start_date']})
        if 'end_date' in date_filters:
            queryset = queryset.filter(**{f'{date_field_name}__lte': date_filters['end_date']})
        return queryset


class GeneralWarehouseReportView(ReportAPIView, UserPermissionsMixin):
    """
    General warehouse movement report.Required: warehouse_id
    Optional: start_date, end_date
    """
    pdf_template_name = 'reports/general_warehouse_report.html'
    warehouse_field_lookup = 'warehouse__in'

    def get(self, request, *args, **kwargs):
        warehouse_id = request.query_params.get('warehouse_id')

        if not warehouse_id:
            return Response({"error": "warehouse_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        date_filters = self.get_date_filters()

        supplies_qs = self.add_date_filters(
            SupplyOperation.objects.filter(warehouse=warehouse_id), 'operation_date', date_filters
        )
        print(f"supplies_qs fedr{supplies_qs.first()}")
        dispatches_qs = self.add_date_filters(
            ExportOperation.objects.filter(warehouse=warehouse_id), 'operation_date', date_filters
        )
        supply_returns_qs = self.add_date_filters(
            ReturnSupplyOperation.objects.filter(original_operation__warehouse=warehouse_id), 'operation_date', date_filters
        )

        dispatches_returns_qs = self.add_date_filters(
            ReturnDispatchOperation.objects.filter(original_operation__warehouse = warehouse_id) , 'operation_date', date_filters
        )
        damage_qs = self.add_date_filters(
            DamageOperation.objects.filter(warehouse = warehouse_id), 'operation_date', date_filters
        )


        returns = {
            'supply_returns': supply_returns_qs.prefetch_related('returned_items__item', 'original_operation'),
            'dispatch_returns': dispatches_returns_qs.prefetch_related('returned_items__item', 'original_operation'),
        }
        data = {
            'supplies': supplies_qs.prefetch_related('items__item', 'supplier'),
            'dispatches': dispatches_qs.prefetch_related('items__item', 'beneficiary'),
            'returns':returns,
            'damages': damage_qs.prefetch_related('items__item', 'warehouse'),
        }

        serializer = GeneralWarehouseReportSerializer(instance=data)
        return Response(serializer.data)

class WarehouseStatusReportView(ReportAPIView):
    """
        The items status report in a specific warehouse.
        Requires: warehouse_id
    """

    pdf_template_name = 'reports//item_status_report.html' 
    def get(self, request, *args, **kwargs):
        warehouse_id = request.query_params.get('warehouse_id')
        if not warehouse_id:
            return Response({"error": "warehouse_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        date_filters = self.get_date_filters()
        queryset = self.add_date_filters(
            InventoryWarehouseitem.objects.filter(warehouse_id=warehouse_id), 
            'last_updated', 
            date_filters
        ).prefetch_related('item', 'warehouse')
        serializer = WarehouseItemStatusSerializer(queryset, many=True)

        response = Response(serializer.data)

        if request.accepted_renderer.format == 'xlsx':
            response['Content-Disposition'] = f'attachment; filename="report_status_warehouse_{warehouse_id}_{datetime.now().strftime("%Y%m%d")}.xlsx"'
        if request.accepted_renderer.format == 'pdf':
            response['Content-Disposition'] = f'attachment; filename="report_status_warehouse_{warehouse_id}_{datetime.now().strftime("%Y%m%d")}.pdf"'
        return response
    
    

class ItemStatusReportView(ReportAPIView):
    """
        The item status report in a all warehouse.
        Requires: item_id
    """
    pdf_template_name = 'reports//item_status_report.html' 

    def get(self, request, *args, **kwargs):
        item_id = request.query_params.get('item_id')
        if not item_id:
            return Response({"error": "item_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        date_filters = self.get_date_filters()

        queryset = self.add_date_filters(
            InventoryWarehouseitem.objects.filter(item=item_id), 
            'last_updated', 
            date_filters
        ).prefetch_related('item', 'warehouse')

        serializer = WarehouseItemStatusSerializer(queryset, many=True)
        
        response = Response(serializer.data)

        if request.accepted_renderer.format == 'xlsx':
            response['Content-Disposition'] = f'attachment; filename="report_status_item_{item_id}_{datetime.now().strftime("%Y%m%d")}.xlsx"'
        if request.accepted_renderer.format == 'pdf':
            response['Content-Disposition'] = f'attachment; filename="report_status_item_{item_id}_{datetime.now().strftime("%Y%m%d")}.pdf"'
        return response
    


class SupplierOperationsReportView(ReportAPIView):
    """
        Incoming operations report for a specific supplier.
        Requires: supplier_id
    """

    pdf_template_name = 'reports//supply_by_station_report.html' 


    def get(self, request, *args, **kwargs):
        supplier_id = request.query_params.get('supplier_id')
        if not supplier_id:
            return Response({"error": "supplier_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        date_filters = self.get_date_filters()
        queryset = self.add_date_filters(
            SupplyOperation.objects.filter(supplier_id=supplier_id), 'operation_date', date_filters
        ).prefetch_related('items__item', 'warehouse')
        
        serializer = ReportSupplySerializer(queryset, many=True)
        response = Response(serializer.data)

        if request.accepted_renderer.format == 'xlsx':
            response['Content-Disposition'] = f'attachment; filename="report_supplier_{supplier_id}_{datetime.now().strftime("%Y%m%d")}.xlsx"'
        if request.accepted_renderer.format == 'pdf':
            response['Content-Disposition'] = f'attachment; filename="report_supplier_{supplier_id}_{datetime.now().strftime("%Y%m%d")}.pdf"'
        return response
    

class BeneficiaryOperationsReportView(ReportAPIView):
    """
        Incoming operations report for a specific beneficiary.
        Requires: beneficiary_id
    """

    pdf_template_name = 'reports//general_beneficiary_report.html' 

    def get(self, request, *args, **kwargs):
        beneficiary_id = request.query_params.get('beneficiary_id')
        if not beneficiary_id:
            return Response({"error": "beneficiary_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        beneficiary_id = request.query_params.get('beneficiary_id')
        if not beneficiary_id:
            return Response({"error": "beneficiary_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        date_filters = self.get_date_filters()
        queryset = self.add_date_filters(
            ExportOperation.objects.filter(beneficiary=beneficiary_id), 'operation_date', date_filters
        ).prefetch_related('items__item', 'warehouse')
        
        serializer = ReportExportSerializer(queryset, many=True)
        response = Response(serializer.data)

        if request.accepted_renderer.format == 'xlsx':
            response['Content-Disposition'] = f'attachment; filename="report_beneficiary_{beneficiary_id}_{datetime.now().strftime("%Y%m%d")}.xlsx"'
        if request.accepted_renderer.format == 'pdf':
            response['Content-Disposition'] = f'attachment; filename="report_beneficiary_{beneficiary_id}_{datetime.now().strftime("%Y%m%d")}.pdf"'
        return response
    
class StationsOperationsReportView(ReportAPIView):
    """
        Incoming operations report for a specific stations.
        Requires: stations_id
    """

    pdf_template_name = 'reports//supply_by_station_report.html' 
    def get(self, request, *args, **kwargs):
        stations_id = request.query_params.get('stations_id')
        if not stations_id:
            return Response({"error": "stations_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        date_filters = self.get_date_filters()
        queryset = self.add_date_filters(
            SupplyOperation.objects.filter(stations=stations_id), 'operation_date', date_filters
        ).prefetch_related('items__item', 'warehouse')
        
        serializer = ReportSupplySerializer(queryset, many=True)
        response = Response(serializer.data)
        if request.accepted_renderer.format == 'xlsx':
            response['Content-Disposition'] = f'attachment; filename="report_stations_{stations_id}_{datetime.now().strftime("%Y%m%d")}.xlsx"'
        if request.accepted_renderer.format == 'pdf':
            response['Content-Disposition'] = f'attachment; filename="report_stations_{stations_id}_{datetime.now().strftime("%Y%m%d")}.pdf"'
            
        return response


class GeneralItemOperationsReportView(ReportAPIView):
    """
    General item movement report. Requires: item_id.
    Optional: start_date, end_date.
    """

    pdf_template_name = 'reports//general_items_report.html' 

    def get(self, request, *args, **kwargs):
        item_id = request.query_params.get('item_id')
        if not item_id:
            return Response({"error": "item_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        date_filters = self.get_date_filters()


        supplies_qs = self.add_date_filters(
            SupplyOperation.objects.filter(items__item_id=item_id),
            'operation_date',
            date_filters
        )

        dispatches_qs = self.add_date_filters(
            ExportOperation.objects.filter(items__item_id=item_id),
            'operation_date',
            date_filters
        )

        supply_returns_qs = self.add_date_filters(
            ReturnSupplyOperation.objects.filter(returned_items__item_id=item_id),
            'operation_date',
            date_filters
        )
        
        dispatch_returns_qs = self.add_date_filters(
            ReturnDispatchOperation.objects.filter(returned_items__item_id=item_id),
            'operation_date',
            date_filters
        )

        damage_qs = self.add_date_filters(
            DamageOperation.objects.filter(items__item_id=item_id),
            'operation_date',
            date_filters
        )

        transfers_from_qs = self.add_date_filters(
            TransferOperation.objects.filter(items__item_id=item_id),
            'operation_date',
            date_filters
        )
        
        returns = {
            'supply_returns': supply_returns_qs.prefetch_related('returned_items__item', 'original_operation__warehouse'),
            'dispatch_returns': dispatch_returns_qs.prefetch_related('returned_items__item', 'original_operation__warehouse'),
        }

        data = {
            'supplies': supplies_qs.prefetch_related('items__item', 'supplier', 'warehouse'),
            'dispatches': dispatches_qs.prefetch_related('items__item', 'beneficiary', 'warehouse'),
            'returns':returns,
            'damages': damage_qs.prefetch_related('items__item', 'warehouse'),
            'transfers_from': transfers_from_qs.prefetch_related('items__item', 'from_warehouse', 'to_warehouse'),
        }

        serializer = GeneralItemReportSerializer(instance=data)
        
        response = Response(serializer.data)
        if request.accepted_renderer.format == 'xlsx':
            response['Content-Disposition'] = f'attachment; filename="report_item_{item_id}_{datetime.now().strftime("%Y%m%d")}.xlsx"'
        if request.accepted_renderer.format == 'pdf':
            response['Content-Disposition'] = f'attachment; filename="report_item_{item_id}_{datetime.now().strftime("%Y%m%d")}.pdf"'
            
        return response

