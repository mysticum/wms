from django.db import models
from django.contrib.auth.models import User

# Topology models

class Warehouse(models.Model):
  name = models.CharField(max_length=45, unique=True)
  code = models.CharField(max_length=45, unique=True)
  address = models.CharField(max_length=45)

  class Meta:
    verbose_name_plural = 'Warehouses'

  def __str__(self):
    return self.name + ' (' + self.code + ')'

class Department(models.Model):
  number = models.CharField(max_length=45)
  name = models.CharField(max_length=45)
  refrigeration_mode = models.IntegerField(null=True, blank=True)
  is_not_topologed = models.BooleanField(default=True)
  warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)

  class Meta:
    verbose_name_plural = 'Departments'

  def __str__(self):
    return self.name + ' - ' + self.warehouse.name

class Row(models.Model):
  number = models.IntegerField()
  department = models.ForeignKey(Department, on_delete=models.CASCADE)

  class Meta:
    verbose_name_plural = 'Rows'

  def __str__(self):
    return str(self.number) + ' - ' + self.department.name + ' - ' + self.department.warehouse.name

class Section(models.Model):
  number = models.CharField(max_length=45)
  row = models.ForeignKey(Row, on_delete=models.CASCADE)

  class Meta:
    verbose_name_plural = 'Sections'

class Level(models.Model):
  number = models.CharField(max_length=45)
  section = models.ForeignKey(Section, on_delete=models.CASCADE)

  class Meta:
    verbose_name_plural = 'Levels'

class Cell(models.Model):
  number = models.IntegerField()
  barcode = models.CharField(max_length=45)
  type = models.IntegerField()
  level = models.ForeignKey(Level, on_delete=models.CASCADE)

  class Meta:
    verbose_name_plural = 'Cells'

# Inventory models

class Product(models.Model):
  name = models.CharField(max_length=100)
  unit_price = models.DecimalField(max_digits=10, decimal_places=2)
  weight = models.DecimalField(max_digits=10, decimal_places=2)
  ean = models.CharField(max_length=12, unique=True)
  sku = models.CharField(max_length=45, unique=True)
  image = models.ImageField(upload_to='products/', null=True, blank=True)
  description = models.CharField(max_length=45, null=True, blank=True)
  package_of_product = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
  package_max_quantity = models.IntegerField(null=True, blank=True)

  class Meta:
    verbose_name_plural = 'Products'

  def __str__(self):
    return self.name + ' (' + self.sku + ')'

class Inventory(models.Model):
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  cell = models.ForeignKey(Cell, on_delete=models.CASCADE)
  expiration_date = models.DateField()
  serie = models.CharField(max_length=45)
  quantity_in_package = models.IntegerField()
  placed_at = models.DateTimeField(auto_now_add=True)
  moved_at = models.DateTimeField(auto_now=True)
  checked_at = models.DateTimeField(auto_now=True)

  class Meta:
    verbose_name_plural = 'Inventories'

# Administrative models

class AppUser(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  role = models.CharField(max_length=10)
  warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)

  class Meta: 
    verbose_name_plural = 'AppUsers'

class DocumentType(models.Model):
  group = models.CharField(max_length=45)
  symbol = models.CharField(max_length=10)
  is_fixing = models.BooleanField()
  name = models.CharField(max_length=45)
  description = models.CharField(max_length=45, null=True, blank=True)
  is_requiring_verification = models.BooleanField()

  class Meta:
    verbose_name_plural = 'DocumentTypes'

  def __str__(self):
    return self.group + " -- " + self.symbol + " " + self.name

class Document(models.Model):
  type = models.ForeignKey(DocumentType, on_delete=models.CASCADE)
  number = models.CharField(max_length=45, unique=True)
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
  verified_by = models.ForeignKey(AppUser, on_delete=models.CASCADE, null=True, blank=True, related_name='document_verifier')
  created_by = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='document_creator')
  status = models.CharField(max_length=45, null=True, blank=True)
  linked_document = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

  class Meta:
    verbose_name_plural = 'Documents'

class Task(models.Model):
  document_type = models.ForeignKey(DocumentType, on_delete=models.CASCADE, null=True, blank=True)
  assigned_by = models.ForeignKey(AppUser, on_delete=models.CASCADE)
  inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, null=True, blank=True)
  first_cell = models.ForeignKey(Cell, on_delete=models.CASCADE, null=True, blank=True, related_name='first_cell')
  second_cell = models.ForeignKey(Cell, on_delete=models.CASCADE, null=True, blank=True, related_name='second_cell')
  document = models.ForeignKey(Document, on_delete=models.CASCADE, null=True, blank=True)
  status = models.CharField(max_length=45)
  created_at = models.DateTimeField(auto_now_add=True)
  started_at = models.DateTimeField(auto_now=True)
  completed_at = models.DateTimeField(auto_now=True)

  class Meta:
    verbose_name_plural = 'Tasks'

# Docs has Products

class Document_has_Product(models.Model):
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  document = models.ForeignKey(Document, on_delete=models.CASCADE)
  amount_added = models.IntegerField()
  amount_required = models.IntegerField(null=True, blank=True)
  unit_price = models.DecimalField(max_digits=10, decimal_places=2)

  class Meta:
    verbose_name_plural = 'Documents_has_Products'
