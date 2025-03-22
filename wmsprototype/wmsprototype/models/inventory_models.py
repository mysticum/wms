from django.db import models

class Product(models.Model):
  name = models.Charfield(max_length=100)
  unit_price = models.DecimalField(max_digits=10, decimal_places=2)
  weight = models.DecimalField(max_digits=10, decimal_places=2)
  ean = models.CharField(max_length=13)
  scu = models.CharField(max_length=20)
  description = models.CharField(max_length=45)
  package_of_product = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
  package_max_quantity = models.IntegerField(null=True, blank=True)

class Inventory(models.Model):
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  cell = models.ForeignKey("topology_models.Cell", on_delete=models.CASCADE)
  expiration_date = models.DateField()
  serie = models.CharField(max_length=45)
  quantity_in_package = models.IntegerField()
  placed_at = models.TimeStampField(auto_now_add=True)
  moved_at = models.TimeStampField(auto_now=True)
  checked_at = models.TimeStampField(auto_now=True)

