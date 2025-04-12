"""
Operational document creator module for populating the database with FVO, TRO, and MMO documents
"""
from django.utils import timezone
import random
import datetime
from wmsprototype.models import (
    Document, DocumentType, DocumentProduct, Department, 
    Product, AppUser, Cell, Address
)
from wmsprototype.services import DocumentService

def create_fvo_documents(command, start_date, end_date, count=20):
    """Create FVO documents (orders to transfer outside the system) and FV responses"""
    command.stdout.write('Creating FVO documents and FV responses...')
    
    # Get document types
    fvo_type = DocumentType.objects.get(symbol='FVO')
    fv_type = DocumentType.objects.get(symbol='FV')
    
    # Get departments
    departments = list(Department.objects.all().order_by('?')[:5])
    
    # Get users
    users = list(AppUser.objects.all())
    default_user = users[0]
    
    # Get products with inventory items
    products_with_inventory = []
    for dept in departments:
        # Get cells in this department
        cells = Cell.objects.filter(level__section__row__department=dept)
        if cells.exists():
            for cell in cells:
                # Check for products in this cell
                for dp in DocumentProduct.objects.filter(cell=cell):
                    # Make sure we're not adding duplicates
                    product_exists = False
                    for p in products_with_inventory:
                        if p.id == dp.product.id:
                            product_exists = True
                            break
                    if not product_exists:
                        products_with_inventory.append(dp.product)
    
    if not products_with_inventory:
        command.stdout.write(command.style.WARNING('No products with inventory found! Skipping FVO creation.'))
        return
        
    # Create addresses for external recipients
    addresses = []
    for _ in range(min(10, count)):
        addresses.append(command.create_slovak_address())
    
    # Create FVO documents (orders for external transfers)
    for i in range(count):
        # Select random department
        dept = random.choice(departments)
        
        # Generate a date between start and end
        doc_date = start_date + datetime.timedelta(
            seconds=random.randint(0, int((end_date - start_date).total_seconds()))
        )
        
        # Create FVO document (order)
        doc_number = DocumentService.generate_document_number(fvo_type, dept)
        
        fvo_doc = Document.objects.create(
            document_type=fvo_type,
            document_number=doc_number,
            current_status='Created',
            total_quantity=0,  # Will update after adding products
            created_by=random.choice(users),
            created_at=doc_date,
            updated_at=doc_date,
            origin_department=dept,
            carrier=f"Carrier-{random.randint(100, 999)}",
            post_barcode=f"LABEL-{random.randint(10000, 99999)}",
            address=random.choice(addresses)
        )
        
        # Generate barcode
        fvo_doc.barcode = DocumentService.generate_barcode(
            fvo_type, doc_number, doc_date.year, 
            doc_date.month, dept.number
        )
        fvo_doc.save()
        
        # Select 1-5 random products to add to the document
        selected_products = random.sample(
            products_with_inventory,
            min(random.randint(1, 5), len(products_with_inventory))
        )
        
        total_qty = 0
        product_details = []  # Store details to create FV document later
        
        # Add products to the FVO document
        for product in selected_products:
            # Get a cell with this product
            cells_with_product = []
            for dp in DocumentProduct.objects.filter(product=product, cell__level__section__row__department=dept):
                if dp.cell not in cells_with_product:
                    cells_with_product.append(dp.cell)
            
            if not cells_with_product:
                continue
                
            cell = random.choice(cells_with_product)
            
            # Random quantity between 1 and 10
            quantity = random.randint(1, 10)
            total_qty += quantity
            
            # Create document product
            dp = DocumentProduct.objects.create(
                document=fvo_doc,
                product=product,
                amount_required=quantity,
                amount_added=0,  # Initially 0, will update when creating FV
                cell=cell,
                unit_price=product.unit_price,
                expiration_date=doc_date + datetime.timedelta(days=random.randint(30, 180)),
                serial=f"LOT-{random.randint(1000, 9999)}"
            )
            
            product_details.append({
                'product': product,
                'quantity': quantity,
                'cell': cell,
                'unit_price': product.unit_price,
                'expiration_date': dp.expiration_date,
                'serial': dp.serial
            })
        
        # Update total quantity
        fvo_doc.total_quantity = total_qty
        fvo_doc.save()
        
        command.stdout.write(f'Created FVO document {fvo_doc.barcode} with {total_qty} products')
        
        # Sometimes create matching FV document (50% chance)
        if random.random() < 0.5 and product_details:
            # FV document should be created a bit later
            fv_date = doc_date + datetime.timedelta(hours=random.randint(1, 48))
            if fv_date > timezone.now():
                # Skip creating FV document if it would be in the future
                continue
            
            # Create FV document (execution)
            doc_number = DocumentService.generate_document_number(fv_type, dept)
            
            fv_doc = Document.objects.create(
                document_type=fv_type,
                document_number=doc_number,
                current_status='Completed',
                total_quantity=total_qty,
                created_by=random.choice(users),
                created_at=fv_date,
                updated_at=fv_date,
                origin_department=dept,
                carrier=fvo_doc.carrier,
                post_barcode=fvo_doc.post_barcode,
                address=fvo_doc.address,
                linked_document=fvo_doc  # Reference to original order
            )
            
            # Generate barcode
            fv_doc.barcode = DocumentService.generate_barcode(
                fv_type, doc_number, fv_date.year, 
                fv_date.month, dept.number
            )
            fv_doc.save()
            
            # Add the same products to the FV document
            for item in product_details:
                dp = DocumentProduct.objects.create(
                    document=fv_doc,
                    product=item['product'],
                    amount_required=item['quantity'],
                    amount_added=item['quantity'],  # Fully fulfilled
                    cell=item['cell'],
                    unit_price=item['unit_price'],
                    expiration_date=item['expiration_date'],
                    serial=item['serial']
                )
            
            # Apply the changes to update inventory
            DocumentService.apply_changes(fv_doc)
            
            # Update FVO to show amounts added
            for dp in fvo_doc.documentproduct_set.all():
                matching_dp = fv_doc.documentproduct_set.filter(product=dp.product).first()
                if matching_dp:
                    dp.amount_added = matching_dp.amount_added
                    dp.save()
            
            command.stdout.write(f'Created FV document {fv_doc.barcode} for FVO {fvo_doc.barcode}')

def create_tro_documents(command, start_date, end_date, count=15):
    """Create TRO documents (transfer orders between warehouses) and WM+/WM- responses"""
    command.stdout.write('Creating TRO documents and WM+/WM- responses...')
    
    # Get document types
    tro_type = DocumentType.objects.get(symbol='TRO')
    wm_plus_type = DocumentType.objects.get(symbol='WM+')
    wm_minus_type = DocumentType.objects.get(symbol='WM-')
    
    # Get departments from different warehouses
    departments = list(Department.objects.all())
    if len(departments) < 2:
        command.stdout.write(command.style.WARNING('Not enough departments for warehouse transfers. Skipping TRO creation.'))
        return
    
    # Group departments by warehouse
    warehouses_to_depts = {}
    for dept in departments:
        wh_id = dept.warehouse.id
        if wh_id not in warehouses_to_depts:
            warehouses_to_depts[wh_id] = []
        warehouses_to_depts[wh_id].append(dept)
    
    # Need at least 2 warehouses
    if len(warehouses_to_depts) < 2:
        command.stdout.write(command.style.WARNING('Not enough warehouses for transfers. Skipping TRO creation.'))
        return
    
    # Get users
    users = list(AppUser.objects.all())
    default_user = users[0]
    
    # Create TRO documents (transfer orders between warehouses)
    for i in range(count):
        # Select source and destination warehouses
        source_wh_id, source_depts = random.choice(list(warehouses_to_depts.items()))
        dest_warehouses = {k: v for k, v in warehouses_to_depts.items() if k != source_wh_id}
        dest_wh_id, dest_depts = random.choice(list(dest_warehouses.items()))
        
        # Select departments
        source_dept = random.choice(source_depts)
        dest_dept = random.choice(dest_depts)
        
        # Generate a date between start and end
        doc_date = start_date + datetime.timedelta(
            seconds=random.randint(0, int((end_date - start_date).total_seconds()))
        )
        
        # Create TRO document (order)
        doc_number = DocumentService.generate_document_number(tro_type, source_dept)
        
        tro_doc = Document.objects.create(
            document_type=tro_type,
            document_number=doc_number,
            current_status='Created',
            total_quantity=0,  # Will update after adding products
            created_by=random.choice(users),
            created_at=doc_date,
            updated_at=doc_date,
            origin_department=source_dept,
            destinate_department=dest_dept,
            carrier=f"Internal-{random.randint(100, 999)}",
            post_barcode=f"WH-TRANSFER-{random.randint(10000, 99999)}"
        )
        
        # Generate barcode
        tro_doc.barcode = DocumentService.generate_barcode(
            tro_type, doc_number, doc_date.year, 
            doc_date.month, source_dept.number
        )
        tro_doc.save()
        
        # Get products in source department with inventory
        products_with_inventory = []
        cells_in_dept = Cell.objects.filter(level__section__row__department=source_dept)
        if cells_in_dept.exists():
            for cell in cells_in_dept:
                for dp in DocumentProduct.objects.filter(cell=cell):
                    # Make sure each product only appears once in our list
                    product_exists = False
                    for p, _ in products_with_inventory:
                        if p.id == dp.product.id:
                            product_exists = True
                            break
                    if not product_exists:
                        products_with_inventory.append((dp.product, cell))
        
        if not products_with_inventory:
            command.stdout.write(command.style.WARNING(f'No products with inventory found in {source_dept}. Skipping this TRO.'))
            continue
        
        # Select 1-5 random products to add to the document (or all if less than 5)
        selected_products = random.sample(
            products_with_inventory,
            min(random.randint(1, 5), len(products_with_inventory))
        )
        
        total_qty = 0
        product_details = []  # Store details to create WM+/WM- documents later
        
        # Add products to the TRO document
        for product, cell in selected_products:
            # Random quantity between 1 and 10
            quantity = random.randint(1, 10)
            total_qty += quantity
            
            # Create document product
            dp = DocumentProduct.objects.create(
                document=tro_doc,
                product=product,
                amount_required=quantity,
                amount_added=0,  # Initially 0, will update when creating WM-/WM+
                cell=cell,
                unit_price=product.unit_price,
                expiration_date=doc_date + datetime.timedelta(days=random.randint(30, 180)),
                serial=f"TR-LOT-{random.randint(1000, 9999)}"
            )
            
            product_details.append({
                'product': product,
                'quantity': quantity,
                'src_cell': cell,
                'unit_price': product.unit_price,
                'expiration_date': dp.expiration_date,
                'serial': dp.serial
            })
        
        # Update total quantity
        tro_doc.total_quantity = total_qty
        tro_doc.save()
        
        command.stdout.write(f'Created TRO document {tro_doc.barcode} for transfer from {source_dept} to {dest_dept}')
        
        # Create WM- and WM+ documents (50% chance)
        if random.random() < 0.5 and product_details:
            # Documents should be created a bit later
            wm_date = doc_date + datetime.timedelta(hours=random.randint(1, 24))
            if wm_date > timezone.now():
                # Skip creating WM documents if they would be in the future
                continue
                
            # Create WM- document (source warehouse deduction)
            wm_minus_number = DocumentService.generate_document_number(wm_minus_type, source_dept)
            
            wm_minus_doc = Document.objects.create(
                document_type=wm_minus_type,
                document_number=wm_minus_number,
                current_status='Completed',
                total_quantity=total_qty,
                created_by=random.choice(users),
                created_at=wm_date,
                updated_at=wm_date,
                origin_department=source_dept,
                carrier=tro_doc.carrier,
                post_barcode=tro_doc.post_barcode,
                linked_document=tro_doc  # Reference to original order
            )
            
            # Generate barcode
            wm_minus_doc.barcode = DocumentService.generate_barcode(
                wm_minus_type, wm_minus_number, wm_date.year, 
                wm_date.month, source_dept.number
            )
            wm_minus_doc.save()
            
            # Add the products to the WM- document
            for item in product_details:
                dp = DocumentProduct.objects.create(
                    document=wm_minus_doc,
                    product=item['product'],
                    amount_required=item['quantity'],
                    amount_added=item['quantity'],  # Fully fulfilled
                    cell=item['src_cell'],
                    unit_price=item['unit_price'],
                    expiration_date=item['expiration_date'],
                    serial=item['serial']
                )
            
            # Create WM+ document (destination warehouse addition)
            # Should be shortly after WM-
            wm_plus_date = wm_date + datetime.timedelta(hours=random.randint(2, 48))
            if wm_plus_date > timezone.now():
                # Apply WM- changes and continue
                DocumentService.apply_changes(wm_minus_doc)
                command.stdout.write(f'Created WM- document {wm_minus_doc.barcode} for TRO {tro_doc.barcode}')
                continue
                
            wm_plus_number = DocumentService.generate_document_number(wm_plus_type, dest_dept)
            
            wm_plus_doc = Document.objects.create(
                document_type=wm_plus_type,
                document_number=wm_plus_number,
                current_status='Completed',
                total_quantity=total_qty,
                created_by=random.choice(users),
                created_at=wm_plus_date,
                updated_at=wm_plus_date,
                origin_department=dest_dept,
                carrier=tro_doc.carrier,
                post_barcode=tro_doc.post_barcode,
                linked_document=tro_doc  # Reference to original order
            )
            
            # Generate barcode
            wm_plus_doc.barcode = DocumentService.generate_barcode(
                wm_plus_type, wm_plus_number, wm_plus_date.year, 
                wm_plus_date.month, dest_dept.number
            )
            wm_plus_doc.save()
            
            # Find default cell in destination department
            dest_cell = None
            if dest_dept.default_cell:
                dest_cell = dest_dept.default_cell
            else:
                dest_cells = Cell.objects.filter(level__section__row__department=dest_dept)
                if dest_cells.exists():
                    dest_cell = dest_cells.first()
            
            if not dest_cell:
                command.stdout.write(command.style.WARNING(f'No cells found in destination department {dest_dept}. Skipping WM+ creation.'))
                # Still apply WM- changes
                DocumentService.apply_changes(wm_minus_doc)
                command.stdout.write(f'Created WM- document {wm_minus_doc.barcode} for TRO {tro_doc.barcode}')
                continue
            
            # Add the products to the WM+ document
            for item in product_details:
                dp = DocumentProduct.objects.create(
                    document=wm_plus_doc,
                    product=item['product'],
                    amount_required=item['quantity'],
                    amount_added=item['quantity'],  # Fully fulfilled
                    cell=dest_cell,  # Use destination cell
                    unit_price=item['unit_price'],
                    expiration_date=item['expiration_date'],
                    serial=item['serial']
                )
            
            # Apply the changes to update inventory
            DocumentService.apply_changes(wm_minus_doc)
            DocumentService.apply_changes(wm_plus_doc)
            
            # Update TRO to show amounts added
            for dp in tro_doc.documentproduct_set.all():
                matching_dp = wm_minus_doc.documentproduct_set.filter(product=dp.product).first()
                if matching_dp:
                    dp.amount_added = matching_dp.amount_added
                    dp.save()
            
            command.stdout.write(f'Created WM- document {wm_minus_doc.barcode} and WM+ document {wm_plus_doc.barcode} for TRO {tro_doc.barcode}')

def create_mmo_documents(command, start_date, end_date, count=15):
    """Create MMO documents (transfer orders within warehouse) and MM responses"""
    command.stdout.write('Creating MMO documents and MM responses...')
    
    # Get document types
    mmo_type = DocumentType.objects.get(symbol='MMO')
    mm_type = DocumentType.objects.get(symbol='MM')
    
    # Get departments with multiple cells
    valid_departments = []
    for dept in Department.objects.all():
        cells = Cell.objects.filter(level__section__row__department=dept)
        if cells.count() >= 2:  # Need at least 2 cells for internal transfer
            valid_departments.append((dept, list(cells)))
    
    if not valid_departments:
        command.stdout.write(command.style.WARNING('No departments with multiple cells found. Skipping MMO creation.'))
        return
    
    # Get users
    users = list(AppUser.objects.all())
    default_user = users[0]
    
    # Create MMO documents (internal transfer orders)
    for i in range(count):
        # Select department with cells
        dept, cells = random.choice(valid_departments)
        
        # Generate a date between start and end
        doc_date = start_date + datetime.timedelta(
            seconds=random.randint(0, int((end_date - start_date).total_seconds()))
        )
        
        # Select source and destination cells
        source_cell = random.choice(cells)
        destination_cells = [c for c in cells if c.id != source_cell.id]
        destination_cell = random.choice(destination_cells)
        
        # Check if source cell has products
        products_with_inventory = []
        for dp in DocumentProduct.objects.filter(cell=source_cell):
            # Make sure we're not adding duplicates
            product_exists = False
            for p in products_with_inventory:
                if p.id == dp.product.id:
                    product_exists = True
                    break
            if not product_exists:
                products_with_inventory.append(dp.product)
        
        if not products_with_inventory:
            continue  # Skip if no products in source cell
        
        # Create MMO document (order)
        doc_number = DocumentService.generate_document_number(mmo_type, dept)
        
        mmo_doc = Document.objects.create(
            document_type=mmo_type,
            document_number=doc_number,
            current_status='Created',
            total_quantity=0,  # Will update after adding products
            created_by=random.choice(users),
            created_at=doc_date,
            updated_at=doc_date,
            origin_department=dept,
            origin_cell=source_cell,
            destinate_cell=destination_cell
        )
        
        # Generate barcode
        mmo_doc.barcode = DocumentService.generate_barcode(
            mmo_type, doc_number, doc_date.year, 
            doc_date.month, dept.number
        )
        mmo_doc.save()
        
        # Select 1-3 random products to add to the document (or all if less than 3)
        selected_products = random.sample(
            products_with_inventory,
            min(random.randint(1, 3), len(products_with_inventory))
        )
        
        total_qty = 0
        product_details = []  # Store details to create MM document later
        
        # Add products to the MMO document
        for product in selected_products:
            # Random quantity between 1 and 5
            quantity = random.randint(1, 5)
            total_qty += quantity
            
            # Create document product
            dp = DocumentProduct.objects.create(
                document=mmo_doc,
                product=product,
                amount_required=quantity,
                amount_added=0,  # Initially 0, will update when creating MM
                cell=source_cell,
                unit_price=product.unit_price,
                expiration_date=doc_date + datetime.timedelta(days=random.randint(30, 180)),
                serial=f"MM-LOT-{random.randint(1000, 9999)}"
            )
            
            product_details.append({
                'product': product,
                'quantity': quantity,
                'unit_price': product.unit_price,
                'expiration_date': dp.expiration_date,
                'serial': dp.serial
            })
        
        # Update total quantity
        mmo_doc.total_quantity = total_qty
        mmo_doc.save()
        
        command.stdout.write(f'Created MMO document {mmo_doc.barcode} for transfer within {dept}')
        
        # Create MM document (70% chance)
        if random.random() < 0.7 and product_details:
            # MM document should be created a bit later
            mm_date = doc_date + datetime.timedelta(hours=random.randint(1, 12))
            if mm_date > timezone.now():
                # Skip creating MM document if it would be in the future
                continue
            
            # Create MM document (execution)
            mm_number = DocumentService.generate_document_number(mm_type, dept)
            
            mm_doc = Document.objects.create(
                document_type=mm_type,
                document_number=mm_number,
                current_status='Completed',
                total_quantity=total_qty,
                created_by=random.choice(users),
                created_at=mm_date,
                updated_at=mm_date,
                origin_department=dept,
                origin_cell=source_cell,
                destinate_cell=destination_cell,
                linked_document=mmo_doc  # Reference to original order
            )
            
            # Generate barcode
            mm_doc.barcode = DocumentService.generate_barcode(
                mm_type, mm_number, mm_date.year, 
                mm_date.month, dept.number
            )
            mm_doc.save()
            
            # Add the products to the MM document
            for item in product_details:
                dp = DocumentProduct.objects.create(
                    document=mm_doc,
                    product=item['product'],
                    amount_required=item['quantity'],
                    amount_added=item['quantity'],  # Fully fulfilled
                    cell=destination_cell,  # Use destination cell for MM
                    unit_price=item['unit_price'],
                    expiration_date=item['expiration_date'],
                    serial=item['serial']
                )
            
            # Apply the changes to update inventory
            DocumentService.apply_changes(mm_doc)
            
            # Update MMO to show amounts added
            for dp in mmo_doc.documentproduct_set.all():
                matching_dp = mm_doc.documentproduct_set.filter(product=dp.product).first()
                if matching_dp:
                    dp.amount_added = matching_dp.amount_added
                    dp.save()
            
            command.stdout.write(f'Created MM document {mm_doc.barcode} for MMO {mmo_doc.barcode}')
