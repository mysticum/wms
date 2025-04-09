from django.utils import timezone
from .models import Document, DocumentStatus, Status


class DocumentService:
    """
    Service class for handling Document-related operations
    """
    
    @staticmethod
    def generate_document_number(document_type, doc_department):
        """
        Generate a sequential document number based on document type and year
        Format: YYYY/TYPE/COUNT
        """
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
    def update_document_status(document, status, user=None, description=None):
        """
        Update a document's status and add to status history
        """
        # Update document's current status
        document.current_status = status.name
        document.save(update_fields=['current_status', 'updated_at'])
        
        # Add to status history
        DocumentStatus.objects.create(
            document=document,
            status=status,
            description=description,
            user=user
        )
        
        # Handle status-specific actions
        if status.name == "Started":
            document.start_at = timezone.now()
            document.save(update_fields=['start_at'])
        elif status.name in ["Completed", "Canceled", "Closed"]:
            document.ended_at = timezone.now()
            document.save(update_fields=['ended_at'])
            
        return True

    @staticmethod
    def apply_document_changes(document):
        if document.document_type.symbol == "BO":
            # Get the default cell of the origin department
            default_cell = document.origin_department.default_cell
            
            if not default_cell:
                raise ValueError(f"Origin department {document.origin_department} has no default cell set")
                
            for dp in document.documentproduct_set.all():
                
                # Create or update an inventory record for this product in the default cell
                from .models import Inventory
                
                # Check if inventory exists for this product in this cell
                inventory, created = Inventory.objects.get_or_create(
                    product=dp.product,
                    cell=default_cell,
                    defaults={
                        'expiration_date': dp.expiration_date,
                        'serial': dp.serial
                    }
                )
                
                # If inventory already existed, update the quantity
                if not created:
                    inventory.quantity_in_package = (inventory.quantity_in_package or 0) + (dp.amount_added or dp.amount_required)
                    inventory.expiration_date = dp.expiration_date or inventory.expiration_date
                    inventory.serial = dp.serial or inventory.serial
                    inventory.save()
    
    @staticmethod
    def prepare_document_for_save(document, user=None):
        """
        Prepare a document for saving by setting required fields
        """
        # If document is new (doesn't have an ID yet)
        if not document.pk:
            document.pk = Document.objects.count() + 1

            # Set document number if not already set
            if not document.document_number:
                document.document_number = DocumentService.generate_document_number(document.document_type, document.origin_department)
            
            # Set created_by if user is provided and created_by is not already set
            if user and not hasattr(document, 'created_by') or not document.created_by:
                document.created_by = user
            
            # Set total_quantity if not already set
            if not hasattr(document, 'total_quantity') or document.total_quantity is None:
                # If document has products, calculate total quantity from them
                if hasattr(document, 'documentproduct_set') and document.documentproduct_set.exists():
                    document.total_quantity = sum(dp.amount_required for dp in document.documentproduct_set.all())
                else:
                    # Default to 0 if no products attached yet
                    document.total_quantity = 0
            
            # Set barcode if not already set
            if not document.barcode:
                # Make sure created_by is set for barcode generation
                if not hasattr(document, 'created_by') or not document.created_by:
                    raise ValueError("Created by user must be set before generating barcode")
                    
                document.barcode = DocumentService.generate_barcode(
                    document.document_type, 
                    ("0" * (4 - len(str(document.document_number))) + str(document.document_number)),
                    str(timezone.now().year)[-2:],
                    ("0" * (2 - len(str(timezone.now().month))) + str(timezone.now().month)),
                    document.origin_department.number
                )
            
            # Set current status if not already set
            if not document.current_status:
                document.current_status = "Created"

            # Apply changes if document is final
            if document.document_type.group == "Sklád":
                DocumentService.apply_document_changes(document)

            
        
        return document
