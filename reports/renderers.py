import pandas as pd
from io import BytesIO
from rest_framework.renderers import BaseRenderer
from django.template.loader import render_to_string
from weasyprint import HTML
from datetime import datetime
import openpyxl

class ExcelRenderer(BaseRenderer):
    """
    Custom renderer for generating Excel (.xlsx) files from report data.
    """
    media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    format = 'xlsx'
    charset = None

    def render(self, data, media_type=None, renderer_context=None):
        if not data or not isinstance(data, dict):
            return b''

        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='openpyxl')

        for sheet_name, sheet_data in data.items():
            if not sheet_data:
                continue

            processed_rows = []
            for record in sheet_data:
                if not isinstance(record, dict):    
                    continue
                base_row = {k: v for k, v in record.items() if k != 'items' and k != 'returned_items'}
                
                print(f">>>>>>>>>>>>>>>>>{record}")
                items = record.get('items') or record.get('returned_items', [])
                print(f"<<<<<<<<<<<<<<<<<<<<<<{items}")
                if items:
                    for item in items:
                        print(f"******************{item}")
                        flat_row = base_row.copy()
                        flat_row['item_name'] = item.get('item_name', item.get('item'))
                        flat_row['quantity'] = item.get('quantity', item.get('quantity'))
                        processed_rows.append(flat_row)
                else:
                    processed_rows.append(base_row)
            
            df = pd.DataFrame(processed_rows)
            
            df.to_excel(writer, sheet_name=sheet_name.title(), index=False)
        writer.close()
        return output.getvalue()



class PdfRenderer(BaseRenderer):
    """
    Custom renderer for generating PDF files from report data using WeasyPrint.
    """
    media_type = 'application/pdf'
    format = 'pdf'
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        view = renderer_context.get('view')
        template_name = getattr(view, 'pdf_template_name', 'reports/default_pdf_template.html')

        context = {
            'report_data': data,
            'current_date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'request': renderer_context.get('request')
        }

        html_string = render_to_string(template_name, context)

        pdf_file = HTML(string=html_string).write_pdf()
        
        return pdf_file
