"""
Additional document creator module for populating the database with RW-, NN+, NN- documents
"""
from django.utils import timezone
import random
import datetime
from wmsprototype.models import (
    Document, DocumentType, DocumentProduct, Department, 
    Product, AppUser, Cell
)
from wmsprototype.services import DocumentService

def create_additional_documents(command, start_date, end_date, count=20):
    """Create RW-, NN+, and NN- documents"""
    # Create return warranty documents (RW-)
    create_rw_documents(command, start_date, end_date, max(5, count // 4))
    
    # Create unplanned additions (NN+)
    create_nn_plus_documents(command, start_date, end_date, max(5, count // 4))
    
    # Create unplanned deductions (NN-)
    create_nn_minus_documents(command, start_date, end_date, max(5, count // 4))

def create_rw_documents(command, start_date, end_date, count):
    """Create RW- documents (warranty returns)"""
    command.stdout.write('Creating RW- documents (warranty returns)...')
    
    # Get document type
    rw_minus_type = DocumentType.objects.get(symbol='RW-')
    
    # Get departments
    departments = list(Department.objects.all())
    if not departments:
        command.stdout.write(command.style.WARNING('No departments found. Skipping RW- document creation.'))
        return
    
    # Get users
    users = list(AppUser.objects.all())
    if not users:
        command.stdout.write(command.style.WARNING('No users found. Skipping RW- document creation.'))
        return
    
    # Create sample addresses for returns
    addresses = []
    for _ in range(min(5, count)):
        addresses.append(command.create_slovak_address())
    
    # Create RW- documents
    for i in range(count):
        # Select a random department
        dept = random.choice(departments)
        
        # Get cells in this department
        cells = Cell.objects.filter(level__section__row__department=dept)
        if not cells.exists():
            continue
            
        # Select a random cell
        cell = random.choice(list(cells))
        
        # Generate a date between start and end
        doc_date = start_date + datetime.timedelta(
            seconds=random.randint(0, int((end_date - start_date).total_seconds()))
        )
        
        # Create RW- document
        doc_number = DocumentService.generate_document_number(rw_minus_type, dept)
        
        rw_doc = Document.objects.create(
            document_type=rw_minus_type,
            document_number=doc_number,
            current_status='Completed',
            total_quantity=0,  # Will update after adding products
            created_by=random.choice(users),
            created_at=doc_date,
            updated_at=doc_date,
            origin_department=dept,
            origin_cell=cell,
            address=random.choice(addresses),
            carrier=f"Warranty-Return-{random.randint(100, 999)}",
            post_barcode=f"WARRANTY-{random.randint(10000, 99999)}",
            description=f"Warranty return for defective products"
        )
        
        # Generate barcode
        rw_doc.barcode = DocumentService.generate_barcode(
            rw_minus_type, doc_number, doc_date.year, 
            doc_date.month, dept.number
        )
        rw_doc.save()
        
        # Get random products
        all_products = list(Product.objects.all().order_by('?')[:3])
        if not all_products:
            command.stdout.write(command.style.WARNING('No products found. Skipping RW- document creation.'))
            return
        
        total_qty = 0
        
        # Add 1-3 products to the document
        for product in all_products:
            # Random quantity between 1 and 5
            quantity = random.randint(1, 5)
            total_qty += quantity
            
            # Random expiration date
            expiry_date = doc_date + datetime.timedelta(days=random.randint(-30, 180))
            
            # Create document product
            dp = DocumentProduct.objects.create(
                document=rw_doc,
                product=product,
                amount_required=quantity,
                amount_added=quantity,  # Fully fulfilled
                cell=cell,
                unit_price=product.unit_price,
                expiration_date=expiry_date,
                serial=f"RW-{random.randint(1000, 9999)}"
            )
        
        # Update total quantity
        rw_doc.total_quantity = total_qty
        rw_doc.save()
        
        # Apply the changes to update inventory
        DocumentService.apply_changes(rw_doc)
        
        command.stdout.write(f'Created RW- document {rw_doc.barcode} with {total_qty} products')

def create_nn_plus_documents(command, start_date, end_date, count):
    """Create NN+ documents (unplanned additions)"""
    command.stdout.write('Creating NN+ documents (unplanned additions)...')
    
    # Get document type
    nn_plus_type = DocumentType.objects.get(symbol='NN+')
    
    # Get departments
    departments = list(Department.objects.all())
    if not departments:
        command.stdout.write(command.style.WARNING('No departments found. Skipping NN+ document creation.'))
        return
    
    # Get users
    users = list(AppUser.objects.all())
    if not users:
        command.stdout.write(command.style.WARNING('No users found. Skipping NN+ document creation.'))
        return
    
    # Create NN+ documents
    for i in range(count):
        # Select a random department
        dept = random.choice(departments)
        
        # Get cells in this department
        cells = Cell.objects.filter(level__section__row__department=dept)
        if not cells.exists() and not dept.default_cell:
            continue
            
        # Select a cell (either a random one or the default)
        if cells.exists():
            cell = random.choice(list(cells))
        else:
            cell = dept.default_cell
        
        # Generate a date between start and end
        doc_date = start_date + datetime.timedelta(
            seconds=random.randint(0, int((end_date - start_date).total_seconds()))
        )
        
        # Create NN+ document
        doc_number = DocumentService.generate_document_number(nn_plus_type, dept)
        
        nn_doc = Document.objects.create(
            document_type=nn_plus_type,
            document_number=doc_number,
            current_status='Completed',
            total_quantity=0,  # Will update after adding products
            created_by=random.choice(users),
            created_at=doc_date,
            updated_at=doc_date,
            origin_department=dept,
            origin_cell=cell,
            description=f"Unplanned product addition - inventory correction"
        )
        
        # Generate barcode
        nn_doc.barcode = DocumentService.generate_barcode(
            nn_plus_type, doc_number, doc_date.year, 
            doc_date.month, dept.number
        )
        nn_doc.save()
        
        # Get random products
        all_products = list(Product.objects.all().order_by('?')[:3])
        if not all_products:
            command.stdout.write(command.style.WARNING('No products found. Skipping NN+ document creation.'))
            return
        
        total_qty = 0
        
        # Add 1-3 products to the document
        for product in all_products:
            # Random quantity between 1 and 10
            quantity = random.randint(1, 10)
            total_qty += quantity
            
            # Random expiration date in the future
            expiry_date = doc_date + datetime.timedelta(days=random.randint(30, 365))
            
            # Create document product
            dp = DocumentProduct.objects.create(
                document=nn_doc,
                product=product,
                amount_required=quantity,
                amount_added=quantity,  # Fully fulfilled
                cell=cell,
                unit_price=product.unit_price,
                expiration_date=expiry_date,
                serial=f"NN-{random.randint(1000, 9999)}"
            )
        
        # Update total quantity
        nn_doc.total_quantity = total_qty
        nn_doc.save()
        
        # Apply the changes to update inventory
        DocumentService.apply_changes(nn_doc)
        
        command.stdout.write(f'Created NN+ document {nn_doc.barcode} with {total_qty} products')

def create_nn_minus_documents(command, start_date, end_date, count):
    """Create NN- documents (unplanned deductions)"""
    command.stdout.write('Creating NN- documents (unplanned deductions)...')
    
    # Get document type
    nn_minus_type = DocumentType.objects.get(symbol='NN-')
    
    # Get departments with inventory
    departments_with_inventory = set()
    for dp in DocumentProduct.objects.all():
        if dp.cell and dp.cell.level and dp.cell.level.section and dp.cell.level.section.row and dp.cell.level.section.row.department:
            departments_with_inventory.add(dp.cell.level.section.row.department)
    
    departments = list(departments_with_inventory)
    if not departments:
        command.stdout.write(command.style.WARNING('No departments with inventory found. Skipping NN- document creation.'))
        return
    
    # Get users
    users = list(AppUser.objects.all())
    if not users:
        command.stdout.write(command.style.WARNING('No users found. Skipping NN- document creation.'))
        return
    
    # Create NN- documents
    for i in range(count):
        # Select a random department with inventory
        dept = random.choice(departments)
        
        # Get cells in this department with inventory
        cells_with_inventory = set()
        for dp in DocumentProduct.objects.all():
            if dp.cell and dp.cell.level and dp.cell.level.section and dp.cell.level.section.row and dp.cell.level.section.row.department and dp.cell.level.section.row.department.id == dept.id:
                cells_with_inventory.add(dp.cell)
        
        if not cells_with_inventory:
            continue
            
        # Select a random cell with inventory
        cell = random.choice(list(cells_with_inventory))
        
        # Generate a date between start and end
        doc_date = start_date + datetime.timedelta(
            seconds=random.randint(0, int((end_date - start_date).total_seconds()))
        )
        
        # Create NN- document
        doc_number = DocumentService.generate_document_number(nn_minus_type, dept)
        
        nn_doc = Document.objects.create(
            document_type=nn_minus_type,
            document_number=doc_number,
            current_status='Completed',
            total_quantity=0,  # Will update after adding products
            created_by=random.choice(users),
            created_at=doc_date,
            updated_at=doc_date,
            origin_department=dept,
            origin_cell=cell,
            description=f"Unplanned product deduction - inventory correction"
        )
        
        # Generate barcode
        nn_doc.barcode = DocumentService.generate_barcode(
            nn_minus_type, doc_number, doc_date.year, 
            doc_date.month, dept.number
        )
        nn_doc.save()
        
        # Get products in this cell
        products_in_cell = []
        for dp in DocumentProduct.objects.filter(cell=cell):
            if dp.product and dp.product not in products_in_cell:
                products_in_cell.append(dp.product)
        
        if not products_in_cell:
            command.stdout.write(command.style.WARNING(f'No products found in cell {cell}. Skipping this NN- document.'))
            nn_doc.delete()
            continue
        
        # Select 1-3 random products from the cell
        selected_products = random.sample(
            products_in_cell,
            min(random.randint(1, 3), len(products_in_cell))
        )
        
        total_qty = 0
        
        # Add products to the document
        for product in selected_products:
            # Random quantity between 1 and 5
            quantity = random.randint(1, 5)
            total_qty += quantity
            
            # Find an existing document product for expiry date and serial
            existing_dp = DocumentProduct.objects.filter(product=product, cell=cell).first()
            expiry_date = existing_dp.expiration_date if existing_dp and existing_dp.expiration_date else None
            serial = existing_dp.serial if existing_dp and existing_dp.serial else f"NN-{random.randint(1000, 9999)}"
            
            # Create document product
            dp = DocumentProduct.objects.create(
                document=nn_doc,
                product=product,
                amount_required=quantity,
                amount_added=quantity,  # Fully fulfilled
                cell=cell,
                unit_price=product.unit_price,
                expiration_date=expiry_date,
                serial=serial
            )
        
        # Update total quantity
        nn_doc.total_quantity = total_qty
        nn_doc.save()
        
        # Apply the changes to update inventory
        DocumentService.apply_changes(nn_doc)
        
        command.stdout.write(f'Created NN- document {nn_doc.barcode} with {total_qty} products')
