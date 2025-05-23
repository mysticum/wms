# Generated by Django 5.1.7 on 2025-04-04 16:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_line', models.CharField(max_length=45)),
                ('second_line', models.CharField(blank=True, max_length=45, null=True)),
                ('city', models.CharField(max_length=45)),
                ('postcode', models.CharField(max_length=45)),
                ('country', models.CharField(max_length=45)),
                ('receiver', models.CharField(blank=True, max_length=45, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=45, null=True)),
                ('email', models.EmailField(blank=True, max_length=45, null=True)),
            ],
            options={
                'verbose_name': 'Address',
                'verbose_name_plural': 'Addresses',
                'db_table': 'Addresses',
            },
        ),
        migrations.CreateModel(
            name='Cell',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('barcode', models.CharField(blank=True, max_length=45, null=True)),
                ('type', models.CharField(blank=True, max_length=45, null=True)),
            ],
            options={
                'verbose_name': 'Cell',
                'verbose_name_plural': 'Cells',
                'db_table': 'Cells',
            },
        ),
        migrations.CreateModel(
            name='DocumentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.CharField(max_length=45)),
                ('symbol', models.CharField(max_length=10, unique=True)),
                ('name', models.CharField(max_length=45)),
                ('description', models.CharField(blank=True, max_length=45, null=True)),
                ('is_for_managers', models.BooleanField()),
            ],
            options={
                'verbose_name': 'Document Type',
                'verbose_name_plural': 'Document Types',
                'db_table': 'Document_types',
            },
        ),
        migrations.CreateModel(
            name='Level',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=45)),
            ],
            options={
                'verbose_name': 'Level',
                'verbose_name_plural': 'Levels',
                'db_table': 'Levels',
            },
        ),
        migrations.CreateModel(
            name='AppUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(max_length=45)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'AppUser',
                'verbose_name_plural': 'AppUsers',
            },
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=45)),
                ('name', models.CharField(max_length=100)),
                ('is_not_topologed', models.BooleanField(default=True)),
                ('refrigeration_mode', models.IntegerField(blank=True, null=True)),
                ('default_cell', models.ForeignKey(blank=True, db_column='default_cell_id', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='default_department_of', to='wmsprototype.cell')),
            ],
            options={
                'verbose_name': 'Department',
                'verbose_name_plural': 'Departments',
                'db_table': 'Departments',
            },
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('barcode', models.CharField(max_length=45)),
                ('total_quantity', models.IntegerField()),
                ('total_weight', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('total_price', models.FloatField(blank=True, null=True)),
                ('priority', models.IntegerField(blank=True, null=True)),
                ('carrier', models.CharField(blank=True, max_length=45, null=True)),
                ('post_barcode', models.CharField(blank=True, max_length=45, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('start_at', models.DateTimeField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('required_at', models.DateTimeField(blank=True, null=True)),
                ('current_status', models.CharField(max_length=45)),
                ('description', models.TextField(blank=True, null=True)),
                ('address', models.ForeignKey(blank=True, db_column='address_id', null=True, on_delete=django.db.models.deletion.PROTECT, to='wmsprototype.address')),
                ('created_by', models.ForeignKey(db_column='created_by_id', on_delete=django.db.models.deletion.PROTECT, related_name='created_documents', to='wmsprototype.appuser')),
                ('destinate_cell', models.ForeignKey(blank=True, db_column='destinate_cell_id', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='destinate_documents', to='wmsprototype.cell')),
                ('destinate_department', models.ForeignKey(blank=True, db_column='destinate_department_id', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='destinate_documents', to='wmsprototype.department')),
                ('linked_document', models.ForeignKey(blank=True, db_column='linked_document_id', null=True, on_delete=django.db.models.deletion.SET_NULL, to='wmsprototype.document')),
                ('origin_cell', models.ForeignKey(blank=True, db_column='origin_cell_id', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='origin_documents', to='wmsprototype.cell')),
                ('origin_department', models.ForeignKey(db_column='origin_department_id', on_delete=django.db.models.deletion.PROTECT, related_name='origin_documents', to='wmsprototype.department')),
                ('verified_by', models.ForeignKey(blank=True, db_column='verified_by_id', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='verified_documents', to='wmsprototype.appuser')),
                ('document_type', models.ForeignKey(db_column='document_type_id', on_delete=django.db.models.deletion.PROTECT, to='wmsprototype.documenttype')),
            ],
            options={
                'verbose_name': 'Document',
                'verbose_name_plural': 'Documents',
                'db_table': 'Documents',
            },
        ),
        migrations.CreateModel(
            name='DocumentUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appuser', models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, to='wmsprototype.appuser')),
                ('document', models.ForeignKey(db_column='document_id', on_delete=django.db.models.deletion.CASCADE, to='wmsprototype.document')),
            ],
            options={
                'verbose_name': 'Document User Assignment',
                'verbose_name_plural': 'Document User Assignments',
                'db_table': 'Documents_has_Users',
                'unique_together': {('document', 'appuser')},
            },
        ),
        migrations.AddField(
            model_name='document',
            name='assigned_users',
            field=models.ManyToManyField(related_name='assigned_documents', through='wmsprototype.DocumentUser', to='wmsprototype.appuser'),
        ),
        migrations.AddField(
            model_name='cell',
            name='level',
            field=models.ForeignKey(db_column='level_id', on_delete=django.db.models.deletion.PROTECT, to='wmsprototype.level'),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('unit_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('weight', models.IntegerField(blank=True, null=True)),
                ('ean', models.CharField(blank=True, max_length=13, null=True, unique=True)),
                ('sku', models.CharField(blank=True, db_column='scu', max_length=45, null=True)),
                ('description', models.CharField(blank=True, db_column='descriprion', max_length=45, null=True)),
                ('image', models.ImageField(null=True, upload_to='products/')),
                ('package_max_quantity', models.IntegerField(blank=True, null=True)),
                ('package_of_product', models.ForeignKey(blank=True, db_column='package_of_product_id', null=True, on_delete=django.db.models.deletion.SET_NULL, to='wmsprototype.product')),
            ],
            options={
                'verbose_name': 'Product',
                'verbose_name_plural': 'Products',
                'db_table': 'Products',
            },
        ),
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expiration_date', models.DateField(blank=True, null=True)),
                ('serial', models.CharField(blank=True, max_length=45, null=True)),
                ('quantity_in_package', models.IntegerField(blank=True, null=True)),
                ('placed_at', models.DateTimeField(auto_now_add=True)),
                ('moved_at', models.DateTimeField(auto_now=True)),
                ('checked_at', models.DateTimeField(auto_now=True)),
                ('cell', models.ForeignKey(db_column='cell_id', on_delete=django.db.models.deletion.PROTECT, to='wmsprototype.cell')),
                ('product', models.ForeignKey(db_column='product_id', on_delete=django.db.models.deletion.PROTECT, to='wmsprototype.product')),
            ],
            options={
                'verbose_name': 'Inventory',
                'verbose_name_plural': 'Inventories',
                'db_table': 'Inventories',
            },
        ),
        migrations.CreateModel(
            name='Row',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('department', models.ForeignKey(db_column='department_id', on_delete=django.db.models.deletion.PROTECT, to='wmsprototype.department')),
            ],
            options={
                'verbose_name': 'Row',
                'verbose_name_plural': 'Rows',
                'db_table': 'Rows',
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('row', models.ForeignKey(db_column='row_id', on_delete=django.db.models.deletion.PROTECT, to='wmsprototype.row')),
            ],
            options={
                'verbose_name': 'Section',
                'verbose_name_plural': 'Sections',
                'db_table': 'Sections',
            },
        ),
        migrations.AddField(
            model_name='level',
            name='section',
            field=models.ForeignKey(db_column='section_id', on_delete=django.db.models.deletion.PROTECT, to='wmsprototype.section'),
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
                ('document_type', models.ForeignKey(db_column='document_type_id', on_delete=django.db.models.deletion.PROTECT, to='wmsprototype.documenttype')),
            ],
            options={
                'verbose_name': 'Status',
                'verbose_name_plural': 'Statuses',
                'db_table': 'Statuses',
            },
        ),
        migrations.CreateModel(
            name='DocumentStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, db_column='descriprion', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('document', models.ForeignKey(db_column='document_id', on_delete=django.db.models.deletion.CASCADE, to='wmsprototype.document')),
                ('user', models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.PROTECT, to='wmsprototype.appuser')),
                ('status', models.ForeignKey(db_column='status_id', on_delete=django.db.models.deletion.PROTECT, to='wmsprototype.status')),
            ],
            options={
                'verbose_name': 'Document Status History',
                'verbose_name_plural': 'Document Status Histories',
                'db_table': 'Documents_has_Statuses',
                'ordering': ['-created_at'],
                'unique_together': {('document', 'status')},
            },
        ),
        migrations.AddField(
            model_name='document',
            name='statuses',
            field=models.ManyToManyField(related_name='documents', through='wmsprototype.DocumentStatus', to='wmsprototype.status'),
        ),
        migrations.CreateModel(
            name='Warehouse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45, unique=True)),
                ('code', models.CharField(max_length=45, unique=True)),
                ('address', models.ForeignKey(db_column='address_id', on_delete=django.db.models.deletion.PROTECT, to='wmsprototype.address')),
                ('main_department', models.ForeignKey(blank=True, db_column='main_department_id', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='main_warehouse_of', to='wmsprototype.department')),
            ],
            options={
                'verbose_name': 'Warehouse',
                'verbose_name_plural': 'Warehouses',
                'db_table': 'Warehouses',
            },
        ),
        migrations.AddField(
            model_name='department',
            name='warehouse',
            field=models.ForeignKey(db_column='warehouse_id', on_delete=django.db.models.deletion.PROTECT, to='wmsprototype.warehouse'),
        ),
        migrations.AddField(
            model_name='appuser',
            name='warehouse',
            field=models.ForeignKey(db_column='warehouse_id', on_delete=django.db.models.deletion.PROTECT, to='wmsprototype.warehouse'),
        ),
        migrations.CreateModel(
            name='DocumentProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_required', models.IntegerField()),
                ('amount_added', models.IntegerField(blank=True, null=True)),
                ('unit_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('expiration_date', models.DateField(blank=True, null=True)),
                ('serial', models.CharField(blank=True, max_length=45, null=True)),
                ('cell', models.ForeignKey(blank=True, db_column='cell_id', null=True, on_delete=django.db.models.deletion.SET_NULL, to='wmsprototype.cell')),
                ('document', models.ForeignKey(db_column='document_id', on_delete=django.db.models.deletion.CASCADE, to='wmsprototype.document')),
                ('product', models.ForeignKey(db_column='product_id', on_delete=django.db.models.deletion.PROTECT, to='wmsprototype.product')),
            ],
            options={
                'verbose_name': 'Document Product Item',
                'verbose_name_plural': 'Document Product Items',
                'db_table': 'Documents_has_Products',
                'unique_together': {('document', 'product')},
            },
        ),
    ]
