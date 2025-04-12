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
    def close_inventory(document, request):

        pd = DocumentService.prepare_document_for_first_save(Document(
            document_type = DocumentType.objects.get(symbol="IP+") if document.document_type.symbol == "IPO" else DocumentType.objects.get(symbol="IC+"),
            origin_department = document.origin_department,
            created_by = request.user.appuser,
            linked_document = document
        ))
        pd.save()
        md = DocumentService.prepare_document_for_first_save(Document(
            document_type = DocumentType.objects.get(symbol="IP-") if document.document_type.symbol == "IPO" else DocumentType.objects.get(symbol="IC-"),
            origin_department = document.origin_department,
            created_by = request.user.appuser,
            linked_document = document
        ))
        md.save()

        for dp in document.documentproduct_set.all():
            if dp.amount_required < dp.amount_added:
                DocumentProduct.objects.create(
                    document = pd,
                    product = dp.product,
                    amount_required = dp.amount_required,
                    amount_added = dp.amount_added - dp.amount_required,
                    cell = dp.cell,
                    expiration_date = dp.expiration_date,
                    serial = dp.serial,
                    unit_price = dp.unit_price
                )
            if dp.amount_required > dp.amount_added:
                DocumentProduct.objects.create(
                    document = md,
                    product = dp.product,
                    amount_required = dp.amount_required - dp.amount_added,
                    cell = dp.cell,
                    expiration_date = dp.expiration_date,
                    serial = dp.serial,
                    unit_price = dp.unit_price
                )
                

        

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
                elif document.document_type.symbol in ["IC-", "IP-", "NN-", "FV", "RW-"]:
                    inventory_item = Inventory.objects.filter(
                        product=dp.product,
                        cell = dp.cell,
                        expiration_date = dp.expiration_date,
                        serial = dp.serial
                    ).first()
                    
                    if inventory_item:
                        inventory_item.delete()
                
    
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
        
        current_user = AppUser.objects.filter(user=request.user).first()
        document.verified_by = current_user
        # if document.document_type.is_for_managers == True:
        #     current_user = AppUser.objects.filter(user=request.user).first()
        #     if current_user.role in ["ZAM", "VED", "ADM"]:
        #         document.verified_by = current_user
        #     else:
        #         raise ValueError("User is not authorized to create this type of document")

        if document.document_type.symbol in ["FVO", "ICO", "IPO", "MMO", "TRO"]:
            document.current_status = "Generated"
            DocumentStatus.objects.create(
                document=document,
                status=Status.objects.get(name="Generated", document_type=document.document_type),
                user=request.user.appuser if hasattr(request.user, 'appuser') else None
            )
        else: 
            document.current_status = "Created"

        if document.document_type.symbol == 'FVO':
            wh = Address.objects.filter(department=document.destinate_department).first()
            document.address = wh.address

        if document.document_type.symbol in ["ICO", "IPO"]:
            DocumentService.prepare_inventory(document)

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

    @staticmethod
    def prepare_inventory(document):
        if document.document_type.symbol == "ICO":
            for i in Inventory.objects.filter(cell = document.origin_cell):
                if DocumentProduct.objects.filter(document = document, product = i.product, cell = i.cell, expiration_date = i.expiration_date, serial = i.serial).exists():
                    DocumentProduct.objects.filter(document = document, product = i.product, cell = i.cell, expiration_date = i.expiration_date, serial = i.serial).update(amount_required = F('amount_required') + i.amount)
                else:
                    DocumentProduct.objects.create(
                        document = document,
                        product = i.product,
                        amount_required = i.amount,
                        cell = i.cell,
                        expiration_date = i.expiration_date,
                        serial = i.serial,
                        unit_price = i.product.unit_price
                    )
        if document.document_type.symbol == "TRO":
            for i in Inventory.objects.filter(cell__in = TopologyService.get_cells_by_department(document.origin_department)):
                if DocumentProduct.objects.filter(document = document, product = i.product, cell = i.cell, expiration_date = i.expiration_date, serial = i.serial).exists():
                    DocumentProduct.objects.filter(document = document, product = i.product, cell = i.cell, expiration_date = i.expiration_date, serial = i.serial).update(amount_required = F('amount_required') + i.amount)
                else:
                    DocumentProduct.objects.create(
                        document = document,
                        product = i.product,
                        amount_required = i.amount,
                        cell = i.cell,
                        expiration_date = i.expiration_date,
                        serial = i.serial,
                        unit_price = i.product.unit_price
                    )
                
class TopologyService:
    
    @staticmethod
    def get_department_by_cell(cell):
        try:
            return cell.level.section.row.department
        except AttributeError:
            return None

    @staticmethod
    def is_cell_in_department(cell, department):
        try:
            cell_department = TopologyService.get_department_by_cell(cell)
            return cell_department == department
        except Exception:
            return False

    @staticmethod
    def get_cells_by_department(department):
        """
        Get all Cells located in a specific Department.
        
        Args:
            department: A Department object
            
        Returns:
            QuerySet of Cell objects belonging to the Department
        """
        # Use Django's nested relationships to find all cells
        # Department -> Row -> Section -> Level -> Cell
        try:
            # Get all rows in the department
            rows = department.row_set.all()
            all_cells = []
            
            # For each row, get all sections, then levels, then cells
            for row in rows:
                sections = row.section_set.all()
                for section in sections:
                    levels = section.level_set.all()
                    for level in levels:
                        cells = level.cell_set.all()
                        all_cells.extend(cells)
            
            return all_cells
        except Exception:
            return []