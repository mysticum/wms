from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Document, DocumentProduct, Status, AppUser, Department, Product


class LoginForm(AuthenticationForm):
    """Custom login form with Bootstrap styling"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )


class DocumentForm(forms.ModelForm):
    """Form for Document model with improved validation and layout"""
    
    status = forms.ModelChoiceField(
        queryset=Status.objects.none(),
        required=False,
        help_text="Change the document status"
    )
    
    class Meta:
        model = Document
        fields = [
            'document_type', 'origin_department', 'destinate_department',
            'priority', 'carrier', 'address', 'post_barcode', 
            'required_at', 'description', 'verified_by',
            'origin_cell', 'destinate_cell', 'linked_document'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'required_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        document_type = kwargs.pop('document_type', None)
        super().__init__(*args, **kwargs)
        
        # If we have an instance, customize form for document type
        if self.instance and self.instance.pk:
            document_type = self.instance.document_type
            
            # Set available statuses based on document type
            self.fields['status'].queryset = Status.objects.filter(
                document_type=document_type
            )
        
        # Customize fields based on document type
        if document_type:
            self._customize_for_document_type(document_type)
        
        # General field customization
        if 'origin_department' in self.fields:
            self.fields['origin_department'].queryset = Department.objects.all()
            
        if 'destinate_department' in self.fields:
            self.fields['destinate_department'].queryset = Department.objects.all()
            
        if 'verified_by' in self.fields:
            self.fields['verified_by'].queryset = AppUser.objects.all()
            
        if 'linked_document' in self.fields:
            self.fields['linked_document'].queryset = Document.objects.exclude(pk=self.instance.pk if self.instance and self.instance.pk else None)
            
    def clean(self):
        """Custom validation for the entire form"""
        cleaned_data = super().clean()
        
        # Fix the document_type validation issue by ensuring it's populated from the instance
        if hasattr(self, 'instance') and self.instance and self.instance.document_type:
            cleaned_data['document_type'] = self.instance.document_type
        
        # Add additional validation logic for required fields based on document type
        if 'origin_department' in self.fields and not cleaned_data.get('origin_department'):
            self.add_error('origin_department', 'Origin department is required')
            
        # Add more field validations as needed
        
        return cleaned_data
    
    def _customize_for_document_type(self, document_type):
        """Customize form fields based on document type"""
        # Define which fields are relevant for each document type
        type_fields = {
            'BO': ['origin_department', 'description', 'priority'],
            'MM+': ['origin_department', 'destinate_department', 'destinate_cell', 'linked_document', 'description', 'priority'],
            'MM-': ['origin_department', 'destinate_department', 'destinate_cell', 'linked_document', 'description', 'priority'],
            'FV': ['origin_department', 'carrier', 'address', 'post_barcode', 'linked_document', 'description', 'priority', 'required_at'],
            'IC+': ['origin_department', 'linked_document', 'verified_by', 'description', 'priority'],
            'IC-': ['origin_department', 'linked_document', 'verified_by', 'description', 'priority'],
            'IP+': ['origin_department', 'linked_document', 'verified_by', 'description', 'priority'],
            'IP-': ['origin_department', 'linked_document', 'verified_by', 'description', 'priority'],
            'WM-': ['origin_department', 'destinate_department', 'linked_document', 'verified_by', 'description', 'priority'],
            'WM+': ['origin_department', 'destinate_department', 'linked_document', 'verified_by', 'description', 'priority'],
            'NN+': ['origin_department', 'verified_by', 'description', 'priority'],
            'NN-': ['origin_department', 'verified_by', 'description', 'priority'],
            'PZ': ['origin_department', 'carrier', 'address', 'verified_by', 'description', 'priority', 'required_at'],
            'RW': ['origin_department', 'destinate_department', 'linked_document', 'verified_by', 'description', 'priority', 'required_at'],
        }
        
        # Get fields for this document type, default to all fields if type not found
        relevant_fields = type_fields.get(document_type.symbol, list(self.fields.keys()))
        
        # Remove document_type from validation requirements
        if 'document_type' in self.fields:
            self.fields['document_type'].required = False
        
        # Hide irrelevant fields
        for field_name in list(self.fields.keys()):
            if field_name not in relevant_fields and field_name != 'status':
                self.fields.pop(field_name)


class DocumentProductForm(forms.ModelForm):
    """Form for Document Product items"""
    
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select product-select'})
    )
    
    class Meta:
        model = DocumentProduct
        fields = ['product', 'amount_required', 'amount_added', 'cell', 'expiration_date', 'serial', 'unit_price']
        widgets = {
            'amount_required': forms.NumberInput(attrs={'class': 'form-control amount-required', 'min': 1}),
            'amount_added': forms.NumberInput(attrs={'class': 'form-control amount-added', 'min': 0}),
            'expiration_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'serial': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


DocumentProductFormSet = forms.inlineformset_factory(
    Document, 
    DocumentProduct,
    form=DocumentProductForm,
    extra=1,
    can_delete=True
)
