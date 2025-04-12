from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from wmsprototype.models import (
    Document, DocumentType, DocumentProduct, Department, 
    Product, AppUser, Cell, Address, Inventory
)
from wmsprototype.services import DocumentService, TopologyService
import random
import datetime
from faker import Faker

# Import document creator modules
from .document_creators.operational import create_fvo_documents, create_tro_documents, create_mmo_documents
from .document_creators.inventory import create_inventory_documents
from .document_creators.other import create_additional_documents

# Initialize faker for Slovak addresses
fake = Faker('sk_SK')

class Command(BaseCommand):
    help = 'Populates the database with sample documents for testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=100,
            help='Number of documents to generate for each type (default: 100)'
        )
    
    def handle(self, *args, **options):
        count = options['count']
        
        # Define date range
        start_date = datetime.datetime(2025, 1, 12, tzinfo=timezone.get_current_timezone())
        end_date = datetime.datetime(2025, 5, 1, tzinfo=timezone.get_current_timezone())
        
        try:
            with transaction.atomic():
                # Verify necessary data exists
                self.check_prerequisites()
                
                # Create BO documents for each department
                self.create_bo_documents(start_date)
                
                # Create operational documents (FVO, TRO, MMO)
                self.create_operational_documents(start_date, end_date, count)
                
                # Create inventory documents (ICO, IPO)
                self.create_inventory_documents(start_date, end_date)
                
                # Create other document types (RW-, NN+, NN-)
                self.create_other_documents(start_date, end_date, count)
                
                self.stdout.write(self.style.SUCCESS('Successfully created documents'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            
    def check_prerequisites(self):
        """Verify required data exists before proceeding"""
        # Check departments
        departments = Department.objects.filter(id__in=[1, 2, 3])
        if departments.count() < 3:
            self.stdout.write(self.style.WARNING(f'Warning: Only {departments.count()} departments found. Expected 3.'))
        
        # Check document types
        required_types = ['BO', 'FVO', 'FV', 'TRO', 'WM+', 'WM-', 'MMO', 'MM', 
                         'ICO', 'IPO', 'IC+', 'IC-', 'IP+', 'IP-', 'RW-', 'NN+', 'NN-']
        missing_types = []
        for symbol in required_types:
            if not DocumentType.objects.filter(symbol=symbol).exists():
                missing_types.append(symbol)
        
        if missing_types:
            self.stdout.write(self.style.WARNING(f'Warning: Missing document types: {", ".join(missing_types)}'))
        
        # Check for products
        products_count = Product.objects.count()
        if products_count < 10:
            self.stdout.write(self.style.WARNING(f'Warning: Only {products_count} products found.'))
        
        # Check for users
        users_count = AppUser.objects.count()
        if users_count == 0:
            raise Exception("No AppUsers found in the database. Please create at least one user.")
            
    def create_slovak_address(self):
        """Create a realistic Slovak address"""
        return Address.objects.create(
            first_line=fake.street_address(),
            second_line=f"Poschodie {random.randint(1, 10)}, Byt {random.randint(1, 99)}" if random.choice([True, False, False, False]) else None,
            city=fake.city(),
            postcode=fake.postcode(),
            country='Slovakia',
            receiver=fake.name(),
            phone_number=fake.phone_number(),
            email=fake.email()
        )
    
    def random_future_date(self, base_date, min_minutes=40, max_hours=18):
        """Generate a random future date between min_minutes and max_hours from base_date"""
        min_delta = datetime.timedelta(minutes=min_minutes)
        max_delta = datetime.timedelta(hours=max_hours)
        
        # Random delta between min and max
        delta_seconds = random.randint(
            int(min_delta.total_seconds()),
            int(max_delta.total_seconds())
        )
        
        return base_date + datetime.timedelta(seconds=delta_seconds)
    
    def create_bo_documents(self, start_date):
        """Create BO documents for each department with bakery products"""
        self.stdout.write('Creating BO documents for each department...')
        
        # Get departments (ids 1 to 3)
        departments = Department.objects.filter(id__in=[1, 2, 3])
        
        # Get bakery products
        bakery_products = list(Product.objects.filter(name__contains='Bread').order_by('?'))
        if len(bakery_products) < 5:  # If not enough bakery products are found
            bakery_products = list(Product.objects.all().order_by('?')[:10])  # Get some random products
        
        # Get a default user
        default_user = AppUser.objects.first()
        
        # For each department, create a BO document
        for dept in departments:
            # Create BO document
            bo_type = DocumentType.objects.get(symbol='BO')
            doc_number = DocumentService.generate_document_number(bo_type, dept)
            
            bo_doc = Document.objects.create(
                document_type=bo_type,
                document_number=doc_number,
                current_status='Completed',
                total_quantity=sum(random.randint(10, 100) for _ in range(len(bakery_products))),
                created_by=default_user,
                created_at=start_date,
                updated_at=start_date,
                origin_department=dept,
            )
            
            # Generate barcode
            bo_doc.barcode = DocumentService.generate_barcode(
                bo_type, doc_number, start_date.year, 
                start_date.month, dept.number
            )
            bo_doc.save()
            
            self.stdout.write(f'Created BO document {bo_doc.barcode} for department {dept}')
            
            # Add products to the BO document
            for product in bakery_products:
                # Get a random cell from the department
                if not dept.is_not_topologed and dept.default_cell:
                    cell = dept.default_cell
                else:
                    cell = Cell.objects.filter(level__section__row__department=dept).order_by('?').first()
                    if not cell:
                        cell = dept.default_cell
                
                # Random quantity between 10 and 100
                quantity = random.randint(10, 100)
                
                # Random expiration date 1-30 days in the future
                expiry_days = random.randint(1, 30)
                expiry_date = start_date + datetime.timedelta(days=expiry_days)
                
                # Create document product
                dp = DocumentProduct.objects.create(
                    document=bo_doc,
                    product=product,
                    amount_required=quantity,
                    amount_added=quantity,  # For BO, amount_added equals amount_required
                    cell=cell,
                    unit_price=product.unit_price,
                    expiration_date=expiry_date,
                    serial=f"LOT-{random.randint(1000, 9999)}"
                )
                
                self.stdout.write(f'  - Added {quantity} of {product.name} to {bo_doc.barcode}')
            
            # Apply the changes to actually create the inventory
            DocumentService.apply_changes(bo_doc)
            self.stdout.write(f'Applied BO document {bo_doc.barcode}')
            
    def create_operational_documents(self, start_date, end_date, count):
        """Create FVO, TRO, and MMO documents with their responses"""
        # Create FVO documents and their FV responses
        create_fvo_documents(self, start_date, end_date, count)
        
        # Create TRO documents and their WM+/WM- responses
        create_tro_documents(self, start_date, end_date, count)
        
        # Create MMO documents and their MM responses
        create_mmo_documents(self, start_date, end_date, count)
    
    def create_inventory_documents(self, start_date, end_date):
        """Create ICO/IPO documents and close them"""
        create_inventory_documents(self, start_date, end_date)
    
    def create_other_documents(self, start_date, end_date, count):
        """Create RW-, NN+, and NN- documents"""
        create_additional_documents(self, start_date, end_date, count)
