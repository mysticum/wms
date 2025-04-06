from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import transaction
from .models import Document, DocumentType, Department, DocumentProduct, Product, Status, AppUser, DocumentStatus
from .forms import DocumentForm, DocumentProductFormSet
from .services import DocumentService

def home(request):
  return render(request, "home.html")

def actions(request):
  return render(request, "actions.html")

def select_document_type(request):
  """View for selecting document type before proceeding to create a specific document"""
  document_types = DocumentType.objects.all()
  
  context = {
      'document_types': document_types,
  }
  
  return render(request, "select_document_type.html", context)

def create_specific_document(request, doc_type):
  """Create a specific type of document based on the selected document type"""
  try:
    # Get the document type object using the symbol
    document_type = get_object_or_404(DocumentType, symbol=doc_type)
    
    if request.method == 'POST':
      try:
        with transaction.atomic():
          # Create a new Document instance but don't save it yet
          document = Document(
              document_type=document_type,
              created_by=request.user.appuser if hasattr(request.user, 'appuser') else None
          )
          
          # Use the form to validate and save the document
          form = DocumentForm(request.POST, instance=document, document_type=document_type)
          
          if form.is_valid():
            # Save the document - our signals will handle number/barcode generation
            document = form.save(commit=False)
            
            # Let the service prepare the document (sets number, barcode, etc.)
            document = DocumentService.prepare_document_for_save(document, request.user.appuser if hasattr(request.user, 'appuser') else None)
            document.save()
            
            # Handle product items using formset
            formset = DocumentProductFormSet(request.POST, instance=document)
            
            if formset.is_valid():
              # Save product items
              formset.save()
              
              # Update document total quantity
              total_qty = sum(form.cleaned_data.get('amount_required', 0) or 0 for form in formset.forms if form.cleaned_data and not form.cleaned_data.get('DELETE', False))
              document.total_quantity = total_qty
              document.save(update_fields=['total_quantity'])
              
              # Set initial status - this is handled by signal now, but we ensure it's set
              initial_status = Status.objects.filter(document_type=document_type, name="Created").first()
              if initial_status and not hasattr(document, 'documentstatus_set') or document.documentstatus_set.count() == 0:
                DocumentService.update_document_status(document, initial_status, document.created_by)
              
              messages.success(request, f"Document {document.barcode} created successfully!")
              return redirect('view_document', document_id=document.id)
            else:
              for error in formset.errors:
                messages.error(request, f"Product form error: {error}")
          else:
            for field, errors in form.errors.items():
              for error in errors:
                messages.error(request, f"{field}: {error}")
      
      except Exception as e:
        messages.error(request, f"Error creating document: {str(e)}")
    
    # Create a new form for GET requests
    form = DocumentForm(document_type=document_type)
    formset = DocumentProductFormSet()
    
    # Get all the necessary data for dropdowns
    departments = Department.objects.all()
    products = Product.objects.all()
    
    # Get users for user selections
    from django.contrib.auth.models import User
    users = User.objects.all()
    
    # Get AppUsers for verified_by fields
    appusers = AppUser.objects.all()
    
    # Get potential linked documents depending on document type
    potential_linked_documents = Document.objects.all()
    
    # Context for rendering the template
    context = {
        'document_type': document_type,
        'form': form,
        'formset': formset,
        'departments': departments,
        'products': products,
        'users': users,
        'appusers': appusers,
        'potential_linked_documents': potential_linked_documents
    }
    
    # Render the appropriate template based on document type
    template_name = f"document_types/{doc_type.replace('+', 'plus').replace('-', 'minus')}.html"
    
    # Try the specific template, fall back to generic if needed
    try:
      return render(request, template_name, context)
    except Exception:
      # Fallback to a generic template with conditional sections
      return render(request, "document_types/generic_document.html", context)
      
  except DocumentType.DoesNotExist:
    messages.error(request, f"Document type {doc_type} does not exist")
    return redirect('select_document_type')


def view_document(request, document_id):
  """View a specific document and its details"""
  document = get_object_or_404(Document, id=document_id)
  document_products = DocumentProduct.objects.filter(document=document)
  status_history = DocumentStatus.objects.filter(document=document).order_by('-created_at')
  
  # Get available statuses for this document type
  available_statuses = Status.objects.filter(document_type=document.document_type)
  
  context = {
      'document': document,
      'document_products': document_products,
      'status_history': status_history,
      'available_statuses': available_statuses
  }
  
  return render(request, "document_details.html", context)


@login_required
def update_document(request, document_id):
  """Update an existing document"""
  document = get_object_or_404(Document, id=document_id)
  
  if request.method == 'POST':
    try:
      with transaction.atomic():
        form = DocumentForm(request.POST, instance=document)
        formset = DocumentProductFormSet(request.POST, instance=document)
        
        if form.is_valid() and formset.is_valid():
          # Process status change if provided
          status_id = request.POST.get('status')
          if status_id:
            status = get_object_or_404(Status, id=status_id)
            user = request.user.appuser if hasattr(request.user, 'appuser') else None
            DocumentService.update_document_status(document, status, user)
          
          # Save form
          form.save()
          
          # Save formset
          formset.save()
          
          # Update document total quantity
          total_qty = sum(form.cleaned_data.get('amount_required', 0) or 0 for form in formset.forms if form.cleaned_data and not form.cleaned_data.get('DELETE', False))
          document.total_quantity = total_qty
          document.save(update_fields=['total_quantity'])
          
          messages.success(request, f"Document {document.barcode} updated successfully!")
          return redirect('view_document', document_id=document.id)
        else:
          for field, errors in form.errors.items():
            for error in errors:
              messages.error(request, f"{field}: {error}")
          
          for i, errors in enumerate(formset.errors):
            if errors:
              for field, error in errors.items():
                messages.error(request, f"Product {i+1} {field}: {error}")
    
    except Exception as e:
      messages.error(request, f"Error updating document: {str(e)}")
  
  form = DocumentForm(instance=document, document_type=document.document_type)
  formset = DocumentProductFormSet(instance=document)
  
  context = {
      'form': form,
      'formset': formset,
      'document': document,
  }
  
  return render(request, "edit_document.html", context)


@require_POST
@login_required
def change_document_status(request, document_id):
  """Change the status of a document"""
  document = get_object_or_404(Document, id=document_id)
  status_id = request.POST.get('status_id')
  description = request.POST.get('description', '')
  
  if not status_id:
    messages.error(request, "No status selected")
    return redirect('view_document', document_id=document_id)
  
  try:
    status = get_object_or_404(Status, id=status_id)
    user = request.user.appuser if hasattr(request.user, 'appuser') else None
    
    # Use the service to update the status
    DocumentService.update_document_status(document, status, user, description)
    
    messages.success(request, f"Document status updated to {status.name}")
  except Exception as e:
    messages.error(request, f"Error updating status: {str(e)}")
  
  return redirect('view_document', document_id=document_id)


@require_POST
@login_required
def generate_document_barcode(request, document_id):
  """Regenerate barcode for a document"""
  document = get_object_or_404(Document, id=document_id)
  
  try:
    # Generate a new barcode
    barcode = DocumentService.generate_barcode(document.document_type, document.number)
    document.barcode = barcode
    document.save(update_fields=['barcode'])
    
    messages.success(request, f"Barcode regenerated: {barcode}")
  except Exception as e:
    messages.error(request, f"Error generating barcode: {str(e)}")
  
  return redirect('view_document', document_id=document_id)