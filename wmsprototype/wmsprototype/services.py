from django.utils import timezone
from .models import *

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
    def apply_changes(document):
        for dp in document.documentproduct_set.all():
            for i in range(dp.amount_required):
                if document.document_type.symbol in ["BO", "WM+"]:
                    inventory = Inventory.objects.create(
                    product=dp.product,
                    cell = document.origin_department.default_cell,
                    expiration_date = dp.expiration_date,
                    serial = dp.serial,
                    placed_at = timezone.now(),
                    moved_at = timezone.now(),
                    checked_at = timezone.now(),
                )
                elif document.document_type.symbol in ["IC+", "IP+", "NN+", "PZ"]:
                    inventory = Inventory.objects.create(
                        product=dp.product,
                        cell = dp.cell,
                        expiration_date = dp.expiration_date,
                        serial = dp.serial,
                        placed_at = timezone.now(),
                        moved_at = timezone.now(),
                        checked_at = timezone.now(),
                    )
                elif document.document_type.symbol in ["IC-", "IP-", "NN-", "FV"]:
                    inventory_items = Inventory.objects.filter(
                        product=dp.product,
                        cell = dp.cell,
                        expiration_date = dp.expiration_date,
                        serial = dp.serial
                    ).first().delete()
                
    
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
        
        if document.document_type.is_for_managers == True:
            current_user = AppUser.objects.filter(user=request.user).first()
            if current_user.role in ["ZAM", "VED", "ADM"]:
                document.verified_by = current_user
            else:
                raise ValueError("User is not authorized to create this type of document")

        if document.document_type.symbol in ["FVO", "ICO", "IPO", "MMO", "TRO"]:
            document.current_status = "Generated"
        else: 
            document.current_status = "Created"

        if document.document_type.symbol == 'FVO':
            wh = Address.objects.filter(department=document.destinate_department).first()
            document.address = wh.address

        if document.linked_document:
            ld = document.linked_document
            for dp in document.documentproduct_set.all():
                ldp = ld.documentproduct_set.filter(product=dp.product)
                if ldp.exists():
                    ldpc = ldp.amount_added
                    ldp.update(amount_added = dp.amount_required + ldpc)
                else:
                    raise Exception(f"Product {dp.product} not found in {ld} linked document")
            if document.document_type.symbol == 'TRO' or document.document_type.symbol == 'FVO':
                document.address = ld.address
                document.carrier = ld.carrier

        document.created_at = timezone.now()
        document.updated_at = timezone.now()

        return document
