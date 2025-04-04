from django.db import models
from django.contrib.auth.models import User

class Address(models.Model):
    first_line = models.CharField(max_length=45)
    second_line = models.CharField(max_length=45, null=True, blank=True)
    city = models.CharField(max_length=45)
    postcode = models.CharField(max_length=45)
    country = models.CharField(max_length=45)
    receiver = models.CharField(max_length=45, null=True, blank=True)
    phone_number = models.CharField(max_length=45, null=True, blank=True)
    email = models.EmailField(max_length=45, null=True, blank=True)

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'
        db_table = 'Addresses'

    def __str__(self):
        return f"{self.first_line}, {self.city}, {self.postcode}"

class Warehouse(models.Model):
    name = models.CharField(max_length=45, unique=True)
    code = models.CharField(max_length=45, unique=True)
    address = models.ForeignKey(
        Address,
        on_delete=models.PROTECT,
        db_column='address_id'
        )
    main_department = models.ForeignKey(
        'Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='main_warehouse_of',
        db_column='main_department_id'
    )

    class Meta:
        verbose_name = 'Warehouse'
        verbose_name_plural = 'Warehouses'
        db_table = 'Warehouses'

    def __str__(self):
        return f"{self.name} ({self.code})"

class Department(models.Model):
    number = models.CharField(max_length=45)
    name = models.CharField(max_length=100)
    is_not_topologed = models.BooleanField(default=True)
    refrigeration_mode = models.IntegerField(null=True, blank=True)
    default_cell = models.ForeignKey(
        'Cell',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='default_department_of',
        db_column='default_cell_id'
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        db_column='warehouse_id'
    )

    class Meta:
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        db_table = 'Departments'

    def __str__(self):
        warehouse_name = self.warehouse.name if self.warehouse else 'N/A'
        return f"{self.name} - {warehouse_name}"

class Row(models.Model):
    number = models.IntegerField()
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        db_column='department_id'
    )

    class Meta:
        verbose_name = 'Row'
        verbose_name_plural = 'Rows'
        db_table = 'Rows'

    def __str__(self):
        dept_name = self.department.name if self.department else 'N/A'
        wh_name = self.department.warehouse.name if self.department and self.department.warehouse else 'N/A'
        return f"Row {self.number} - {dept_name} - {wh_name}"

class Section(models.Model):
    number = models.IntegerField()
    row = models.ForeignKey(
        Row,
        on_delete=models.PROTECT,
        db_column='row_id'
    )

    class Meta:
        verbose_name = 'Section'
        verbose_name_plural = 'Sections'
        db_table = 'Sections'

    def __str__(self):
        row_num = self.row.number if self.row else 'N/A'
        return f"Section {self.number} (Row: {row_num})"


class Level(models.Model):
    number = models.CharField(max_length=45)
    section = models.ForeignKey(
        Section,
        on_delete=models.PROTECT,
        db_column='section_id'
    )

    class Meta:
        verbose_name = 'Level'
        verbose_name_plural = 'Levels'
        db_table = 'Levels'

    def __str__(self):
        section_num = self.section.number if self.section else 'N/A'
        return f"Level {self.number} (Section: {section_num})"

class Cell(models.Model):
    number = models.IntegerField()
    barcode = models.CharField(max_length=45, null=True, blank=True)
    type = models.CharField(max_length=45, null=True, blank=True)
    level = models.ForeignKey(
        Level,
        on_delete=models.PROTECT,
        db_column='level_id'
    )

    class Meta:
        verbose_name = 'Cell'
        verbose_name_plural = 'Cells'
        db_table = 'Cells'

    def __str__(self):
        level_num = self.level.number if self.level else 'N/A'
        return f"Cell {self.number} (Level: {level_num}, Barcode: {self.barcode or 'None'})"

class Product(models.Model):
    name = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)
    ean = models.CharField(max_length=13, unique=True, null=True, blank=True)
    sku = models.CharField(max_length=45, null=True, blank=True, db_column='scu')
    description = models.CharField(max_length=45, null=True, blank=True, db_column='descriprion')
    image = models.ImageField(upload_to='products/', null=True)
    package_of_product = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='package_of_product_id'
    )
    package_max_quantity = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        db_table = 'Products'

    def __str__(self):
        return f"{self.name} ({self.sku or 'No SKU'})"

class Inventory(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        db_column='product_id'
        )
    cell = models.ForeignKey(
        Cell,
        on_delete=models.PROTECT,
        db_column='cell_id'
        )
    expiration_date = models.DateField(null=True, blank=True)
    serial = models.CharField(max_length=45, null=True, blank=True)
    quantity_in_package = models.IntegerField(null=True, blank=True)
    placed_at = models.DateTimeField(auto_now_add=True)
    moved_at = models.DateTimeField(auto_now=True)
    checked_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Inventory'
        verbose_name_plural = 'Inventories'
        db_table = 'Inventories'

    def __str__(self):
        prod_name = self.product.name if self.product else 'N/A'
        cell_num = self.cell.number if self.cell else 'N/A'
        return f"Inventory ID {self.pk}: {prod_name} in Cell {cell_num}"

class AppUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=45)
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        db_column='warehouse_id'
        )

    class Meta:
        verbose_name = 'AppUser'
        verbose_name_plural = 'AppUsers'

    def __str__(self):
        return self.user.username

class DocumentType(models.Model):
    group = models.CharField(max_length=45)
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=45)
    description = models.CharField(max_length=45, null=True, blank=True)
    is_for_managers = models.BooleanField()

    class Meta:
        verbose_name = 'Document Type'
        verbose_name_plural = 'Document Types'
        db_table = 'Document_types'

    def __str__(self):
        return f"{self.group} -- {self.symbol} {self.name}"

class Status(models.Model):
    document_type = models.ForeignKey(
        DocumentType,
        on_delete=models.PROTECT,
        db_column='document_type_id'
    )
    name = models.CharField(max_length=45)

    class Meta:
        verbose_name = 'Status'
        verbose_name_plural = 'Statuses'
        db_table = 'Statuses'

    def __str__(self):
        doc_type_name = self.document_type.name if self.document_type else 'N/A'
        return f"{self.name} (Type: {doc_type_name})"


class Document(models.Model):
    document_type = models.ForeignKey(
        DocumentType,
        on_delete=models.PROTECT,
        db_column='document_type_id'
    )
    document_number = models.IntegerField()
    barcode = models.CharField(max_length=45)
    origin_department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='origin_documents',
        db_column='origin_department_id'
    )
    destinate_department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='destinate_documents',
        db_column='destinate_department_id'
    )
    total_quantity = models.IntegerField()
    total_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_price = models.FloatField(null=True, blank=True)
    priority = models.IntegerField(null=True, blank=True)
    carrier = models.CharField(max_length=45, null=True, blank=True)
    address = models.ForeignKey(
        Address,
        on_delete=models.PROTECT,
        null=True, blank=True,
        db_column='address_id'
    )
    post_barcode = models.CharField(max_length=45, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    start_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    required_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        AppUser,
        on_delete=models.PROTECT,
        related_name='created_documents',
        db_column='created_by_id'
    )
    verified_by = models.ForeignKey(
        AppUser,
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='verified_documents',
        db_column='verified_by_id'
    )
    current_status = models.CharField(max_length=45)
    linked_document = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        db_column='linked_document_id'
    )
    origin_cell = models.ForeignKey(
        Cell,
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='origin_documents',
        db_column='origin_cell_id'
    )
    destinate_cell = models.ForeignKey(
        Cell,
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='destinate_documents',
        db_column='destinate_cell_id'
    )
    description = models.TextField(null=True, blank=True)
    assigned_users = models.ManyToManyField(
        AppUser,
        related_name='assigned_documents',
        through='DocumentUser'
    )
    statuses = models.ManyToManyField(
        Status,
        through='DocumentStatus',
        related_name='documents'
    )

    class Meta:
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
        db_table = 'Documents'

    def __str__(self):
        doc_type_symbol = self.document_type.symbol if self.document_type else 'N/A'
        return f"Doc {self.document_number} (Type: {doc_type_symbol})"

class DocumentProduct(models.Model):
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        db_column='document_id'
        )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        db_column='product_id'
        )
    amount_required = models.IntegerField()
    amount_added = models.IntegerField(null=True, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cell = models.ForeignKey(
        Cell,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        db_column='cell_id'
    )
    expiration_date = models.DateField(null=True, blank=True)
    serial = models.CharField(max_length=45, null=True, blank=True)

    class Meta:
        verbose_name = 'Document Product Item'
        verbose_name_plural = 'Document Product Items'
        db_table = 'Documents_has_Products'
        unique_together = ('document', 'product')

    def __str__(self):
        doc_num = self.document.document_number if self.document else 'N/A'
        prod_name = self.product.name if self.product else 'N/A'
        return f"Doc {doc_num} - Product {prod_name} (Req: {self.amount_required})"


class DocumentUser(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, db_column='document_id')
    appuser = models.ForeignKey(AppUser, on_delete=models.CASCADE, db_column='user_id')

    class Meta:
        db_table = 'Documents_has_Users'
        unique_together = ('document', 'appuser')
        verbose_name = 'Document User Assignment'
        verbose_name_plural = 'Document User Assignments'

    def __str__(self):
        doc_num = self.document.document_number if self.document else 'N/A'
        user_name = self.appuser.user.username if self.appuser and self.appuser.user else 'N/A'
        return f"Doc {doc_num} assigned to User {user_name}"


class DocumentStatus(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, db_column='document_id')
    status = models.ForeignKey(Status, on_delete=models.PROTECT, db_column='status_id')
    description = models.TextField(null=True, blank=True, db_column='descriprion')
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        AppUser,
        on_delete=models.PROTECT,
        db_column='user_id'
    )

    class Meta:
        db_table = 'Documents_has_Statuses'
        unique_together = ('document', 'status')
        verbose_name = 'Document Status History'
        verbose_name_plural = 'Document Status Histories'
        ordering = ['-created_at']

    def __str__(self):
        doc_num = self.document.document_number if self.document else 'N/A'
        status_name = self.status.name if self.status else 'N/A'
        user_name = self.user.user.username if self.user and self.user.user else 'N/A'
        ts = self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else 'N/A'
        return f"Doc {doc_num} - Status '{status_name}' set by {user_name} at {ts}"
