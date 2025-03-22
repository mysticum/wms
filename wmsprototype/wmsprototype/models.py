from django.db import models

# Topology models

class Warehouse(models.Model):
  name = models.CharField(max_length=45)
  code = models.CharField(max_length=45)
  address = models.CharField(max_length=45)

class Department(models.Model):
  number = models.CharField(max_length=45)
  name = models.CharField(max_length=45)
  refrigeration_mode = models.IntegerField()
  warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)

class Row(models.Model):
  number = models.CharField(max_length=45)
  department = models.ForeignKey(Department, on_delete=models.CASCADE)

class Section(models.Model):
  number = models.CharField(max_length=45)
  row = models.ForeignKey(Row, on_delete=models.CASCADE)

class Level(models.Model):
  number = models.CharField(max_length=45)
  section = models.ForeignKey(Section, on_delete=models.CASCADE)

class Cell(models.Model):
  number = models.IntegerField()
  barcode = models.CharField(max_length=45)
  type = models.IntegerField()
  level = models.ForeignKey(Level, on_delete=models.CASCADE)

# Inventory models

class Product(models.Model):
  name = models.CharField(max_length=100)
  unit_price = models.DecimalField(max_digits=10, decimal_places=2)
  weight = models.DecimalField(max_digits=10, decimal_places=2)
  ean = models.CharField(max_length=13)
  scu = models.CharField(max_length=20)
  description = models.CharField(max_length=45)
  package_of_product = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
  package_max_quantity = models.IntegerField(null=True, blank=True)

class Inventory(models.Model):
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  cell = models.ForeignKey(Cell, on_delete=models.CASCADE)
  expiration_date = models.DateField()
  serie = models.CharField(max_length=45)
  quantity_in_package = models.IntegerField()
  placed_at = models.DateTimeField(auto_now_add=True)
  moved_at = models.DateTimeField(auto_now=True)
  checked_at = models.DateTimeField(auto_now=True)

# Administrative models

class User(models.Model):
  login = models.CharField(max_length=45)
  password = models.CharField(max_length=45)
  first_name = models.CharField(max_length=45)
  last_name = models.CharField(max_length=45)
  role = models.IntegerField()

class DocumentType(models.Model):
  group = models.CharField(max_length=45)
  symbol = models.CharField(max_length=10)
  is_fixing = models.BooleanField()
  name = models.CharField(max_length=45)
  description = models.CharField(max_length=45, null=True, blank=True)
  is_requiring_verification = models.BooleanField()

class Document(models.Model):
  type = models.ForeignKey(DocumentType, on_delete=models.CASCADE)
  number = models.CharField(max_length=45)
  original_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='original_warehouse')
  destination_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, null=True, blank=True, related_name='destination_warehouse')
  total_quantity = models.IntegerField(null=True, blank=True)
  total_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
  post_barcode = models.CharField(max_length=45, null=True, blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  start_at = models.DateTimeField(null=True, blank=True)
  updated_at = models.DateTimeField(null=True, blank=True)
  ended_at = models.DateTimeField(null=True, blank=True)
  required_at = models.DateTimeField(null=True, blank=True)
  verified_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='document_verifier')
  created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='document_creator')
  status = models.CharField(max_length=45, null=True, blank=True)
  linked_document = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

class Task(models.Model):
    document_type = models.ForeignKey(DocumentType, on_delete=models.CASCADE, null=True, blank=True)
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE)
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, null=True, blank=True)
    first_cell = models.ForeignKey(Cell, on_delete=models.CASCADE, null=True, blank=True, related_name='first_cell')
    second_cell = models.ForeignKey(Cell, on_delete=models.CASCADE, null=True, blank=True, related_name='second_cell')
    document = models.ForeignKey(Document, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=45)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(auto_now=True)

# Docs has Products

class Documents_has_Products(models.Model):
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  document = models.ForeignKey(Document, on_delete=models.CASCADE)
  amount_required = models.IntegerField()
  amount_added = models.IntegerField()
  unit_price = models.DecimalField(max_digits=10, decimal_places=2)
