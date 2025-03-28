# Generated by Django 5.1.7 on 2025-03-22 15:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wmsprototype', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=45)),
                ('name', models.CharField(max_length=45)),
                ('refrigeration_mode', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='DocumentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.CharField(max_length=45)),
                ('symbol', models.CharField(max_length=10)),
                ('is_fixing', models.BooleanField()),
                ('name', models.CharField(max_length=45)),
                ('description', models.CharField(blank=True, max_length=45, null=True)),
                ('is_requiring_verification', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Level',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=45)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login', models.CharField(max_length=45)),
                ('password', models.CharField(max_length=45)),
                ('first_name', models.CharField(max_length=45)),
                ('last_name', models.CharField(max_length=45)),
                ('role', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Warehouse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
                ('code', models.CharField(max_length=45)),
                ('address', models.CharField(max_length=45)),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=45)),
                ('total_quantity', models.IntegerField(blank=True, null=True)),
                ('total_weight', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('post_barcode', models.CharField(blank=True, max_length=45, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('start_at', models.DateTimeField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('required_at', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(blank=True, max_length=45, null=True)),
                ('linked_document', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='wmsprototype.document')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wmsprototype.documenttype')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='document_creator', to='wmsprototype.user')),
                ('verified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='document_verifier', to='wmsprototype.user')),
                ('destination_warehouse', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='destination_warehouse', to='wmsprototype.warehouse')),
                ('original_warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='original_warehouse', to='wmsprototype.warehouse')),
            ],
        ),
        migrations.CreateModel(
            name='Cell',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('barcode', models.CharField(max_length=45)),
                ('type', models.IntegerField()),
                ('level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wmsprototype.level')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('weight', models.DecimalField(decimal_places=2, max_digits=10)),
                ('ean', models.CharField(max_length=13)),
                ('scu', models.CharField(max_length=20)),
                ('description', models.CharField(max_length=45)),
                ('package_max_quantity', models.IntegerField(blank=True, null=True)),
                ('package_of_product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='wmsprototype.product')),
            ],
        ),
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expiration_date', models.DateField()),
                ('serie', models.CharField(max_length=45)),
                ('quantity_in_package', models.IntegerField()),
                ('placed_at', models.DateTimeField(auto_now_add=True)),
                ('moved_at', models.DateTimeField(auto_now=True)),
                ('checked_at', models.DateTimeField(auto_now=True)),
                ('cell', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wmsprototype.cell')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wmsprototype.product')),
            ],
        ),
        migrations.CreateModel(
            name='Documents_has_Products',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_required', models.IntegerField()),
                ('amount_added', models.IntegerField()),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wmsprototype.document')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wmsprototype.product')),
            ],
        ),
        migrations.CreateModel(
            name='Row',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=45)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wmsprototype.department')),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=45)),
                ('row', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wmsprototype.row')),
            ],
        ),
        migrations.AddField(
            model_name='level',
            name='section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wmsprototype.section'),
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=45)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('started_at', models.DateTimeField(auto_now=True)),
                ('completed_at', models.DateTimeField(auto_now=True)),
                ('document', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='wmsprototype.document')),
                ('document_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='wmsprototype.documenttype')),
                ('first_cell', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='first_cell', to='wmsprototype.cell')),
                ('inventory', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='wmsprototype.inventory')),
                ('second_cell', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='second_cell', to='wmsprototype.cell')),
                ('assigned_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wmsprototype.user')),
            ],
        ),
        migrations.AddField(
            model_name='department',
            name='warehouse',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wmsprototype.warehouse'),
        ),
    ]
