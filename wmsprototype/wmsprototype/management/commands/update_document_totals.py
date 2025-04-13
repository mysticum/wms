from django.core.management.base import BaseCommand
from django.db import transaction
from wmsprototype.models import Document, DocumentProduct
from decimal import Decimal

class Command(BaseCommand):
    help = 'Updates total_price and total_weight for all documents where these values are missing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update of all documents, even if they already have values'
        )
        parser.add_argument(
            '--doc-id',
            type=int,
            help='Update specific document by ID'
        )
        parser.add_argument(
            '--doc-barcode',
            type=str,
            help='Update specific document by barcode'
        )
    
    def handle(self, *args, **options):
        force_update = options['force']
        doc_id = options['doc_id']
        doc_barcode = options['doc_barcode']
        
        # Get documents to update
        if doc_id:
            # Update specific document by ID
            documents = Document.objects.filter(id=doc_id)
            if not documents.exists():
                self.stdout.write(self.style.ERROR(f'Document with ID {doc_id} not found'))
                return
        elif doc_barcode:
            # Update specific document by barcode
            documents = Document.objects.filter(barcode=doc_barcode)
            if not documents.exists():
                self.stdout.write(self.style.ERROR(f'Document with barcode {doc_barcode} not found'))
                return
        else:
            # Get all documents or only those with missing values
            if force_update:
                documents = Document.objects.all()
            else:
                documents = Document.objects.filter(
                    total_price__isnull=True
                ) | Document.objects.filter(
                    total_weight__isnull=True
                )
        
        total_count = documents.count()
        updated_count = 0
        skipped_count = 0
        
        self.stdout.write(f'Found {total_count} documents to process')
        
        # Process each document
        with transaction.atomic():
            for doc in documents:
                try:
                    updated = self.update_document_totals(doc, force_update)
                    if updated:
                        updated_count += 1
                    else:
                        skipped_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error updating document {doc.barcode}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(
            f'Processed {total_count} documents: '
            f'{updated_count} updated, {skipped_count} skipped'
        ))
    
    def update_document_totals(self, document, force_update):
        """
        Update total_price and total_weight for a document based on its products
        Returns True if document was updated, False otherwise
        """
        # Check if update is needed
        price_needs_update = document.total_price is None or force_update
        weight_needs_update = document.total_weight is None or force_update
        
        if not price_needs_update and not weight_needs_update:
            return False
        
        # Get all document products
        doc_products = DocumentProduct.objects.filter(document=document)
        if not doc_products.exists():
            # No products to calculate from
            return False
        
        # Calculate totals
        total_price = Decimal('0.00')
        total_weight = Decimal('0.00')
        
        for dp in doc_products:
            # For price calculation
            if dp.unit_price is not None:
                quantity = dp.amount_added or dp.amount_required or 0
                item_price = dp.unit_price * quantity
                total_price += item_price
            
            # For weight calculation
            if dp.product.weight is not None:
                quantity = dp.amount_added or dp.amount_required or 0
                item_weight = Decimal(dp.product.weight) * quantity / Decimal('1000')  # Convert to kg
                total_weight += item_weight
        
        # Update the document
        if price_needs_update and total_price > 0:
            document.total_price = float(total_price)
        
        if weight_needs_update and total_weight > 0:
            document.total_weight = total_weight
        
        document.save()
        
        self.stdout.write(f'Updated {document.barcode}: '
                        f'Price={document.total_price}, '
                        f'Weight={document.total_weight}')
        return True
