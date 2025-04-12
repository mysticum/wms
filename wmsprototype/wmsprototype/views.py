from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import transaction
from .models import *
from .forms import DocumentForm, DocumentProductFormSet, LoginForm
from .services import DocumentService

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
    return render(request, "home.html")


@login_required(login_url='login')
def actions(request):
    return render(request, "actions.html")

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
def view_document(request, document_id):
  """View a specific document and handle status changes"""
  document = get_object_or_404(Document, id=document_id)
  
  # Get available statuses for this document type
  available_statuses = Status.objects.filter(document_type=document.document_type)
  
  if request.method == 'POST' and 'change_status' in request.POST:
    new_status_id = request.POST.get('new_status')
    if new_status_id:
      try:
        new_status = Status.objects.get(id=new_status_id)
        
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
  
  context = {
    'document': document,
    'available_statuses': available_statuses,
    'status_history': status_history,
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
