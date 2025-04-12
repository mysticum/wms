"""
Inventory document creator module for populating the database with ICO, IPO, IC+, IC-, IP+, IP- documents
"""
from django.utils import timezone
import random
import datetime
from wmsprototype.models import (
    Document, DocumentType, DocumentProduct, Department, 
    Product, AppUser, Cell, Address, DocumentUser
)
from wmsprototype.services import DocumentService

def create_inventory_documents(command, start_date, end_date):
    """Create ICO/IPO documents (inventory orders) and their related documents"""
    command.stdout.write('Creating inventory documents...')
    
    # Get document types
    ico_type = DocumentType.objects.get(symbol='ICO')  # Partial inventory
    ipo_type = DocumentType.objects.get(symbol='IPO')  # Full inventory
    ic_plus_type = DocumentType.objects.get(symbol='IC+')  # Partial inventory surplus
    ic_minus_type = DocumentType.objects.get(symbol='IC-')  # Partial inventory shortage
    ip_plus_type = DocumentType.objects.get(symbol='IP+')  # Full inventory surplus
    ip_minus_type = DocumentType.objects.get(symbol='IP-')  # Full inventory shortage
    
    # Get departments
    departments = list(Department.objects.all())
    if not departments:
        command.stdout.write(command.style.WARNING('No departments found. Skipping inventory document creation.'))
        return
    
    # Get users for inventory committee
    users = list(AppUser.objects.all())
    if len(users) < 2:
        command.stdout.write(command.style.WARNING('Not enough users for inventory committee. Skipping inventory document creation.'))
        return
    
    # Create partial inventory (ICO) documents - one per department
    create_partial_inventory_documents(command, ico_type, ic_plus_type, ic_minus_type, departments, users, start_date, end_date)
    
    # Create full inventory (IPO) documents - for a few random departments
    create_full_inventory_documents(command, ipo_type, ip_plus_type, ip_minus_type, departments, users, start_date, end_date)

def create_partial_inventory_documents(command, ico_type, ic_plus_type, ic_minus_type, departments, users, start_date, end_date):
    """Create partial inventory documents (ICO and IC+/IC-)"""
    command.stdout.write('Creating partial inventory (ICO) documents...')
    
    for dept in departments:
        # Get cells in this department
        cells = Cell.objects.filter(level__section__row__department=dept)
        if not cells.exists():
            continue
        
        # For partial inventory, select a random cell
        target_cell = random.choice(list(cells))
        
        # Check if the cell has products
        inventory_in_cell = False
        for dp in DocumentProduct.objects.filter(cell=target_cell):
            if dp.product:
                inventory_in_cell = True
                break
                
        if not inventory_in_cell:
            # Skip cells without inventory
            continue
        
        # Generate a date between start and end
        doc_date = start_date + datetime.timedelta(
            seconds=random.randint(0, int((end_date - start_date).total_seconds()))
        )
        
        # Create ICO document (order for partial inventory)
        doc_number = DocumentService.generate_document_number(ico_type, dept)
        
        ico_doc = Document.objects.create(
            document_type=ico_type,
            document_number=doc_number,
            current_status='Created',
            total_quantity=0,  # Will calculate after gathering products
            created_by=random.choice(users),
            created_at=doc_date,
            updated_at=doc_date,
            origin_department=dept,
            origin_cell=target_cell,  # For partial inventory, specify the cell
            description=f"Partial inventory for cell {target_cell.number}"
        )
        
        # Generate barcode
        ico_doc.barcode = DocumentService.generate_barcode(
            ico_type, doc_number, doc_date.year, 
            doc_date.month, dept.number
        )
        ico_doc.save()
        
        # Add inventory committee (2-3 users)
        committee_size = random.randint(2, min(3, len(users)))
        committee = random.sample(users, committee_size)
        for user in committee:
            DocumentUser.objects.create(
                document=ico_doc,
                appuser=user
            )
        
        # Get all products in the cell
        products_in_cell = []
        for dp in DocumentProduct.objects.filter(cell=target_cell):
            product = dp.product
            if product and product not in products_in_cell:
                products_in_cell.append(product)
        
        if not products_in_cell:
            command.stdout.write(command.style.WARNING(f'No products found in cell {target_cell}. Skipping inventory.'))
            continue
        
        total_qty = 0
        product_details = []
        
        # Add products to the ICO document
        for product in products_in_cell:
            # Get the expected quantity from inventory
            expected_qty = random.randint(1, 20)  # Simplified, in reality should be based on actual inventory
            total_qty += expected_qty
            
            # Create document product
            dp = DocumentProduct.objects.create(
                document=ico_doc,
                product=product,
                amount_required=expected_qty,  # Expected quantity
                amount_added=0,  # Will be updated in IC+/IC-
                cell=target_cell,
                unit_price=product.unit_price
            )
            
            product_details.append({
                'product': product,
                'expected_qty': expected_qty,
                'unit_price': product.unit_price
            })
        
        # Update total quantity
        ico_doc.total_quantity = total_qty
        ico_doc.save()
        
        command.stdout.write(f'Created ICO document {ico_doc.barcode} for cell {target_cell.number} in department {dept}')
        
        # 80% chance to create IC+/IC- documents
        if random.random() < 0.8 and product_details:
            # Inventory resolution date should be later
            resolution_date = doc_date + datetime.timedelta(hours=random.randint(2, 48))
            if resolution_date > timezone.now():
                # Skip creating resolution documents if it would be in the future
                continue
            
            # For each product, decide if it has surplus, shortage, or exact match
            results = []
            for item in product_details:
                # Determine the actual quantity (-2 to +2 from expected)
                deviation = random.randint(-2, 2)
                actual_qty = max(0, item['expected_qty'] + deviation)
                
                results.append({
                    'product': item['product'],
                    'expected_qty': item['expected_qty'],
                    'actual_qty': actual_qty,
                    'deviation': deviation,
                    'unit_price': item['unit_price']
                })
            
            # Check if there are any surpluses
            surpluses = [r for r in results if r['deviation'] > 0]
            if surpluses:
                # Create IC+ document for surpluses
                create_inventory_resolution(
                    command, ic_plus_type, dept, target_cell, 
                    surpluses, resolution_date, ico_doc, users
                )
            
            # Check if there are any shortages
            shortages = [r for r in results if r['deviation'] < 0]
            if shortages:
                # Create IC- document for shortages
                create_inventory_resolution(
                    command, ic_minus_type, dept, target_cell, 
                    shortages, resolution_date, ico_doc, users
                )

def create_full_inventory_documents(command, ipo_type, ip_plus_type, ip_minus_type, departments, users, start_date, end_date):
    """Create full inventory documents (IPO and IP+/IP-)"""
    command.stdout.write('Creating full inventory (IPO) documents...')
    
    # Select a few random departments for full inventory
    selected_depts = random.sample(departments, min(2, len(departments)))
    
    for dept in selected_depts:
        # Check if department has products
        cells = Cell.objects.filter(level__section__row__department=dept)
        if not cells.exists():
            continue
        
        has_products = False
        for cell in cells:
            for dp in DocumentProduct.objects.filter(cell=cell):
                if dp.product:
                    has_products = True
                    break
            if has_products:
                break
                
        if not has_products:
            # Skip departments without inventory
            continue
        
        # Generate a date between start and end
        doc_date = start_date + datetime.timedelta(
            seconds=random.randint(0, int((end_date - start_date).total_seconds()))
        )
        
        # Create IPO document (order for full inventory)
        doc_number = DocumentService.generate_document_number(ipo_type, dept)
        
        ipo_doc = Document.objects.create(
            document_type=ipo_type,
            document_number=doc_number,
            current_status='Created',
            total_quantity=0,  # Will calculate after gathering products
            created_by=random.choice(users),
            created_at=doc_date,
            updated_at=doc_date,
            origin_department=dept,
            description=f"Full inventory for department {dept.name}"
        )
        
        # Generate barcode
        ipo_doc.barcode = DocumentService.generate_barcode(
            ipo_type, doc_number, doc_date.year, 
            doc_date.month, dept.number
        )
        ipo_doc.save()
        
        # Add inventory committee (2-4 users)
        committee_size = random.randint(2, min(4, len(users)))
        committee = random.sample(users, committee_size)
        for user in committee:
            DocumentUser.objects.create(
                document=ipo_doc,
                appuser=user
            )
        
        # Get all products in the department
        products_in_dept = []
        cell_map = {}  # Map products to cells
        
        for cell in cells:
            for dp in DocumentProduct.objects.filter(cell=cell):
                product = dp.product
                if product and product not in products_in_dept:
                    products_in_dept.append(product)
                    cell_map[product.id] = cell
        
        if not products_in_dept:
            command.stdout.write(command.style.WARNING(f'No products found in department {dept}. Skipping inventory.'))
            continue
        
        total_qty = 0
        product_details = []
        
        # Add products to the IPO document
        for product in products_in_dept:
            # Get the expected quantity from inventory
            expected_qty = random.randint(5, 50)  # Simplified
            total_qty += expected_qty
            
            # Create document product
            dp = DocumentProduct.objects.create(
                document=ipo_doc,
                product=product,
                amount_required=expected_qty,  # Expected quantity
                amount_added=0,  # Will be updated in IP+/IP-
                cell=cell_map.get(product.id),
                unit_price=product.unit_price
            )
            
            product_details.append({
                'product': product,
                'expected_qty': expected_qty,
                'unit_price': product.unit_price,
                'cell': cell_map.get(product.id)
            })
        
        # Update total quantity
        ipo_doc.total_quantity = total_qty
        ipo_doc.save()
        
        command.stdout.write(f'Created IPO document {ipo_doc.barcode} for department {dept}')
        
        # 80% chance to create IP+/IP- documents
        if random.random() < 0.8 and product_details:
            # Inventory resolution date should be later
            resolution_date = doc_date + datetime.timedelta(hours=random.randint(12, 96))
            if resolution_date > timezone.now():
                # Skip creating resolution documents if it would be in the future
                continue
            
            # For each product, decide if it has surplus, shortage, or exact match
            results = []
            for item in product_details:
                # Determine the actual quantity (-5 to +5 from expected)
                deviation = random.randint(-5, 5)
                actual_qty = max(0, item['expected_qty'] + deviation)
                
                results.append({
                    'product': item['product'],
                    'expected_qty': item['expected_qty'],
                    'actual_qty': actual_qty,
                    'deviation': deviation,
                    'unit_price': item['unit_price'],
                    'cell': item['cell']
                })
            
            # Check if there are any surpluses
            surpluses = [r for r in results if r['deviation'] > 0]
            if surpluses:
                # Create IP+ document for surpluses
                create_inventory_resolution(
                    command, ip_plus_type, dept, None, 
                    surpluses, resolution_date, ipo_doc, users
                )
            
            # Check if there are any shortages
            shortages = [r for r in results if r['deviation'] < 0]
            if shortages:
                # Create IP- document for shortages
                create_inventory_resolution(
                    command, ip_minus_type, dept, None, 
                    shortages, resolution_date, ipo_doc, users
                )

def create_inventory_resolution(command, doc_type, dept, cell, results, doc_date, linked_doc, users):
    """Helper function to create inventory resolution documents (IC+, IC-, IP+, IP-)"""
    doc_number = DocumentService.generate_document_number(doc_type, dept)
    
    # Calculate total quantity
    total_qty = sum(abs(r['deviation']) for r in results)
    
    # Create document
    resolution_doc = Document.objects.create(
        document_type=doc_type,
        document_number=doc_number,
        current_status='Completed',
        total_quantity=total_qty,
        created_by=random.choice(users),
        created_at=doc_date,
        updated_at=doc_date,
        origin_department=dept,
        origin_cell=cell,  # Only set for partial inventory
        linked_document=linked_doc  # Reference to original inventory order
    )
    
    # Generate barcode
    resolution_doc.barcode = DocumentService.generate_barcode(
        doc_type, doc_number, doc_date.year, 
        doc_date.month, dept.number
    )
    resolution_doc.save()
    
    # Add products to the document
    for result in results:
        dp = DocumentProduct.objects.create(
            document=resolution_doc,
            product=result['product'],
            amount_required=abs(result['deviation']),  # The deviation is the amount to adjust
            amount_added=abs(result['deviation']),  # Always fully fulfilled
            cell=result.get('cell', cell),  # Use provided cell or default for document
            unit_price=result['unit_price']
        )
    
    # Apply the changes to update inventory
    DocumentService.apply_changes(resolution_doc)
    
    # Get the symbol for logging
    symbol = resolution_doc.document_type.symbol
    command.stdout.write(f'Created {symbol} document {resolution_doc.barcode} for inventory document {linked_doc.barcode}')
