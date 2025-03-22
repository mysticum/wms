from django.db import models

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