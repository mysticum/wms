from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import transaction
import json
from .models import *
from .forms import DocumentForm, DocumentProductFormSet, LoginForm
from .services import DocumentService, TopologyService, AnalyticsService

def login_view(request):
    """Handle user login"""
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome, {username}!")
                # Redirect to the page user came from or home page
                next_page = request.GET.get('next', 'home')
                return redirect(next_page)
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})


def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')


@login_required(login_url='login')
def home(request):
    # Check if the current user is a manager
    is_admin = AppUser.objects.filter(user=request.user).first().role == "ADM"
    
    # For non-manager users, get open documents of specific types
    open_documents = []
    if not is_admin:
        # Get documents of types FVO, ICO, IPO, MMO, and TRO that are open
        document_types = DocumentType.objects.filter(symbol__in=['FVO', 'ICO', 'IPO', 'MMO', 'TRO'])
        
        # Get documents with these types that aren't in final statuses (like 'Completed' or 'Cancelled')
        # Assuming 'Completed' and 'Cancelled' are final statuses, adjust based on your actual status names
        open_documents = Document.objects.filter(
            document_type__in=document_types
        ).exclude(
            current_status__in=['Completed', 'Cancelled']
        ).order_by('-created_at')
    
    context = {
        'open_documents': open_documents,
        'is_admin': is_admin
    }
    
    return render(request, "home.html", context)


@login_required(login_url='login')
def actions(request):
    return render(request, "actions.html")

@login_required(login_url='login')
def analytics(request):
    """View for analytics dashboard"""
    # Get suspicious operations
    suspicious_docs = AnalyticsService.get_suspicious_operations()
    
    # Get daily minus totals
    minus_totals = AnalyticsService.get_daily_minus_totals()
    minus_dates = json.dumps([date.strftime('%Y-%m-%d') for date in minus_totals.keys()])
    minus_values = json.dumps(list(minus_totals.values()))
    
    # Get FV document totals
    fv_totals = AnalyticsService.get_daily_fv_totals()
    fv_dates = json.dumps([date.strftime('%Y-%m-%d') for date in fv_totals.keys()])
    fv_values = json.dumps(list(fv_totals.values()))
    
    # Get product freshness
    freshness = AnalyticsService.get_product_freshness()
    freshness_labels = json.dumps(list(freshness.keys()))
    freshness_values = json.dumps(list(freshness.values()))
    
    context = {
        'suspicious_docs': suspicious_docs,
        'minus_dates': minus_dates,
        'minus_values': minus_values,
        'fv_dates': fv_dates,
        'fv_values': fv_values,
        'freshness_labels': freshness_labels,
        'freshness_values': freshness_values,
        'is_current_user_manager': AppUser.objects.filter(user=request.user).first().role in ['ZAM', 'VED', 'ADM']
    }
    
    return render(request, "analytics.html", context)

@login_required(login_url='login')
def select_document_type(request):
  """View for selecting document type before proceeding to create a specific document"""
  document_types = DocumentType.objects.all().order_by('-group', 'symbol')
  
  context = {
      'document_types': document_types,
      'is_current_user_manager': AppUser.objects.filter(user=request.user).first().role in ['ZAM', 'VED', 'ADM']
  }
  
  return render(request, "select_document_type.html", context)

@login_required(login_url='login')
def list_documents(request):
  """View to display all documents in the system"""
  # Get all documents, ordered by creation date (newest first)
  documents = Document.objects.all().order_by('-created_at')
  
  # Filter by document type if specified in query parameters
  doc_type_id = request.GET.get('doc_type')
  if doc_type_id:
    documents = documents.filter(document_type_id=doc_type_id)
  
  # Filter by department if specified in query parameters
  dept_id = request.GET.get('department')
  if dept_id:
    documents = documents.filter(origin_department_id=dept_id)
    
  # Get all document types for the filter dropdown
  document_types = DocumentType.objects.all().order_by('-group', 'symbol')
  
  # Get all departments for the filter dropdown
  departments = Department.objects.all().order_by('name')
  
  context = {
      'documents': documents,
      'document_types': document_types,
      'departments': departments,
      'is_current_user_manager': AppUser.objects.filter(user=request.user).first().role in ['ZAM', 'VED', 'ADM']
  }
  
  return render(request, "documents_list.html", context)

@login_required(login_url='login')
def list_products(request):
  """View to display all products in the system"""
  # Get all products
  products = Product.objects.all().order_by('name')
  
  # Filter by name if specified in query parameters
  product_name = request.GET.get('name')
  if product_name:
    products = products.filter(name__icontains=product_name)
  
  # Filter by EAN if specified
  ean = request.GET.get('ean')
  if ean:
    products = products.filter(ean__icontains=ean)
  
  # Add inventory count to each product
  for product in products:
    product.inventory_count = Inventory.objects.filter(product=product).count()
  
  context = {
    'products': products,
    'is_current_user_manager': AppUser.objects.filter(user=request.user).first().role in ['ZAM', 'VED', 'ADM']
  }
  
  return render(request, "products_list.html", context)

@login_required(login_url='login')
def view_product(request, product_id):
  """View a specific product with inventory balances by department"""
  product = get_object_or_404(Product, id=product_id)
  
  # Get all inventory items for this product
  inventory_items = Inventory.objects.filter(product=product)
  
  # Organize inventory by department
  inventory_by_department = {}
  total_quantity = 0
  
  for item in inventory_items:
    # Get the department for this cell
    department = TopologyService.get_department_by_cell(item.cell)
    
    if department:
      dept_id = department.id
      
      # Initialize department entry if it doesn't exist
      if dept_id not in inventory_by_department:
        inventory_by_department[dept_id] = {
          'department': department,
          'total_quantity': 0,
          'locations': []
        }
      
      # Check if this cell is already in the locations list
      cell_exists = False
      for location in inventory_by_department[dept_id]['locations']:
        if location['cell'].id == item.cell.id:
          location['quantity'] += 1
          cell_exists = True
          break
      
      # If cell not in list, add it
      if not cell_exists:
        inventory_by_department[dept_id]['locations'].append({
          'cell': item.cell,
          'quantity': 1,
          'expiration_date': item.expiration_date,
          'serial': item.serial
        })
      
      # Update department total
      inventory_by_department[dept_id]['total_quantity'] += 1
      total_quantity += 1
  
  context = {
    'product': product,
    'inventory_by_department': inventory_by_department.values(),
    'total_quantity': total_quantity,
    'is_current_user_manager': AppUser.objects.filter(user=request.user).first().role in ['ZAM', 'VED', 'ADM']
  }
  
  return render(request, "view_product.html", context)

def view_document(request, document_id):
  """View a specific document and handle status changes"""
  document = get_object_or_404(Document, id=document_id)
  
  # Get available statuses for this document type
  available_statuses = Status.objects.filter(document_type=document.document_type)
  
  if request.method == 'POST' and 'change_status' in request.POST:
    with transaction.atomic():
      new_status_id = request.POST.get('new_status')
      if new_status_id:
        try:
          new_status = Status.objects.get(id=new_status_id)

          if document.current_status == "Completed":
              raise ValueError("Cannot change status of a completed document")

          if document.document_type.symbol in ["ICO", "IPO"] and new_status.name == "Completed":
            DocumentService.close_inventory(document)          

          # Get user-provided description or leave it empty
          status_description = request.POST.get('status_description', '')
          
          # Record the status change in DocumentStatus
          DocumentStatus.objects.create(
            document=document,
            status=new_status,
            user=request.user.appuser,
            description=status_description
          )
          
          # Update document current status
          document.update_status(new_status)
          
          messages.success(request, f"Document status updated to {new_status.name}")
          return redirect('view_document', document_id=document_id)
        except Exception as e:
          messages.error(request, f"Error updating status: {str(e)}")
  
  # Get status history for the document
  status_history = DocumentStatus.objects.filter(document=document).order_by('-created_at')
  
  # Get documents that link to this document (where this document is the linked_document)
  linked_documents = Document.objects.filter(linked_document=document)
  
  context = {
    'document': document,
    'available_statuses': available_statuses,
    'status_history': status_history,
    'linked_documents': linked_documents,
  }
  
  return render(request, "view_document.html", context)

@login_required(login_url='login')
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

          print("document created")
          
          # Use the form to validate and save the document
          form = DocumentForm(request.POST, instance=document, document_type=document_type)
          print("form created")
          # Check if form is valid first
          if not form.is_valid():
              for field, errors in form.errors.items():
                  for error in errors:
                      messages.error(request, f"Document form error in {field}: {error}")
              raise Exception("The Document could not be created because the data didn't validate.")
          print("form valid")  
          # Save the document - our signals will handle number/barcode generation
          document = form.save(commit=False)
          print("document saved")
          # Let the service prepare the document (sets number, barcode, etc.)
          document = DocumentService.prepare_document_for_first_save(document, request.user.appuser if hasattr(request.user, 'appuser') else None, request)
          print("document prepared")
          document.save()
          print("document saved")
          
          # Handle product items using formset
          formset = DocumentProductFormSet(request.POST, instance=document)
          print("formset created")
          
          if not formset.is_valid():
              print(formset.errors)
              for form_idx, form_errors in enumerate(formset.errors):
                  for field, errors in form_errors.items():
                      messages.error(request, f"Product #{form_idx+1} error in {field}: {errors[0]}")
              raise Exception("The Document could not be created because product data didn't validate.")
          
          if formset.is_valid():
            # Save product items
            formset.save()
            
            # Update document total quantity
            total_qty = sum(form.cleaned_data.get('amount_required', 0) or 0 for form in formset.forms if form.cleaned_data and not form.cleaned_data.get('DELETE', False))
            document.total_quantity = total_qty
            document.save(update_fields=['total_quantity'])

            if document.document_type.group == 'Sklád':
              DocumentService.apply_changes(document)
            
            messages.success(request, f"Document {document.barcode} created successfully!")
            # return redirect('view_document', document_id=document.id)
          else:
            for error in formset.errors:
              messages.error(request, f"Product form error: {error}")

      
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
    appusers = AppUser.objects.all()
    
    # Get cells for cell selection dropdowns
    cells = Cell.objects.all()
    
    # Get potential linked documents depending on document type
    potential_linked_documents = Document.objects.all()

    # Get rows, sections, and levels for cell selection
    rows = Row.objects.all()
    sections = Section.objects.all()
    levels = Level.objects.all()
    
    # Get addresses for address selection dropdown
    addresses = Address.objects.all()
    
    # Context for rendering the template
    context = {
        'document_type': document_type,
        'form': form,
        'formset': formset,
        'departments': departments,
        'rows': rows,
        'sections': sections,
        'levels': levels,
        'cells': cells,
        'products': products,
        'users': users,
        'appusers': appusers,
        'potential_linked_documents': potential_linked_documents,
        'addresses': addresses,
        'is_current_user_manager': AppUser.objects.filter(user=request.user).first().role in ['ZAM', 'VED', 'ADM']
    }
    
    # Render the appropriate template based on document type
    template_name = f"document_types/{doc_type.replace('+', 'plus').replace('-', 'minus')}.html"
    
    # Try the specific template, fall back to generic if needed
    try:
      return render(request, template_name, context)
    except Exception:
      # Fallback to a generic template with conditional sections
      return render(request, "generic_document.html", context)
      
  except DocumentType.DoesNotExist:
    messages.error(request, f"Document type {doc_type} does not exist")
    return redirect('select_document_type')



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
