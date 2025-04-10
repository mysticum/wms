from django.utils import timezone
from .models import Document, DocumentStatus, Status
from .models import Inventory


class DocumentService:

    
    @staticmethod
    def generate_document_number(document_type, doc_department):
        current_year = timezone.now().year
        # Get count of documents for this type in the current year
        count = Document.objects.filter(
            document_type=document_type, 
            created_at__year=current_year,
            origin_department=doc_department
        ).count() + 1
        
        return count
    
    @staticmethod
    def generate_barcode(document_type, document_number, document_year, document_month, document_department_number):
        barcode_value = f"{document_type.symbol}/{document_number}/{document_year}{document_month}/{document_department_number}"
        return barcode_value

    
    @staticmethod
    def prepare_document_for_first_save(document, user=None, request=None):

        document.pk = Document.objects.count() + 1
        document.document_number = DocumentService.generate_document_number(document.document_type, document.origin_department)
        
        if hasattr(document, 'documentproduct_set') and document.documentproduct_set.exists():
            document.total_quantity = sum(x for x in amount_required)
        else:
            # Default to 0 if no products attached yet
            document.total_quantity = 0
             
        document.barcode = DocumentService.generate_barcode(
            document.document_type, 
            ("0" * (4 - len(str(document.document_number))) + str(document.document_number)),
            str(timezone.now().year)[-2:],
            ("0" * (2 - len(str(timezone.now().month))) + str(timezone.now().month)),
            document.origin_department.number
        )
        
        document.current_status = "Created"
        document.created_at = timezone.now()
        document.updated_at = timezone.now()

        return document
