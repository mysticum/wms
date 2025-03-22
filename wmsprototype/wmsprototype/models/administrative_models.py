from django.db import models

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
  original_warehouse = models.ForeignKey("topology_models.Warehouse", on_delete=models.CASCADE)
  destination_warehouse = models.ForeignKey("topology_models.Warehouse", on_delete=models.CASCADE, null=True, blank=True)
  total_quantity = models.IntegerField(null=True, blank=True)
  total_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
  post_barcode = models.CharField(max_length=45, null=True, blank=True)
  created_at = models.TimeStampField(auto_now_add=True)
  start_at = models.TimeStampField(null=True, blank=True)
  updated_at = models.TimeStampField(null=True, blank=True)
  ended_at = models.TimeStampField(null=True, blank=True)
  required_at = models.TimeStampField(null=True, blank=True)
  verifyed_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
  created_by = models.ForeignKey(User, on_delete=models.CASCADE)
  status = models.CharField(max_length=45, null=True, blank=True)
  linked_document = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

class Task(models.Model):
    document_type = models.ForeignKey(DocumentType, on_delete=models.CASCADE, null=True, blank=True)
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE)
    inventory = models.ForeignKey("administrative_models.Inventory", on_delete=models.CASCADE, null=True, blank=True)
    first_cell = models.ForeignKey("topology_models.Cell", on_delete=models.CASCADE, null=True, blank=True)
    second_cell = models.ForeignKey("topology_models.Cell", on_delete=models.CASCADE, null=True, blank=True)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=45)
    created_at = models.TimeStampField(auto_now_add=True)
    started_at = models.TimeStampField(auto_now=True)
    completed_at = models.TimeStampField(auto_now=True)
