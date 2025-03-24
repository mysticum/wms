from django.db import migrations

def create_initial_document_types(apps, schema_editor):
    DocumentType = apps.get_model('wmsprototype', 'DocumentType')
    # Insert a few sample rows
    DocumentType.objects.create(
        group="Shipping",
        symbol="SH",
        is_fixing=False,
        name="Shipping Document",
        description="Shipping documents",
        is_requiring_verification=True,
    )
    DocumentType.objects.create(
        group="Receiving",
        symbol="RC",
        is_fixing=True,
        name="Receiving Document",
        description="Receiving documents",
        is_requiring_verification=False,
    )
    DocumentType.objects.create(
      group="Inventory",
      symbol="BO",
      is_fixing=False,
      name="Additional Inventory",
      description="Additional inventory",
      is_requiring_verification=False,
    )
    DocumentType.objects.create(
      group="Inventory",
      symbol="BZ",
      is_fixing=False,
      name="Inventory Closure",
      description="Inventory closure",
      is_requiring_verification=False,
    )
    DocumentType.objects.create(
      group="Inventory",
      symbol="I+",
      is_fixing=False,
      name="Inventory Surplus",
      description="Inventory surplus",
      is_requiring_verification=False,
    )
    DocumentType.objects.create(
      group="Inventory",
      symbol="I-",
      is_fixing=False,
      name="Inventory Deficit",
      description="Inventory deficit",
      is_requiring_verification=False,
    )
    DocumentType.objects.create(
      group="Inventory",
      symbol="KM+",
      is_fixing=False,
      name="Inventory Exchange - Receipt",
      description="Inventory exchange - receipt",
      is_requiring_verification=False,
    )
    DocumentType.objects.create(
      group="Inventory",
      symbol="KM-",
      is_fixing=False,
      name="Inventory Exchange - Issue",
      description="Inventory exchange - issue",
      is_requiring_verification=False,
    )
    DocumentType.objects.create(
      group="Inventory",
      symbol="MM+",
      is_fixing=False,
      name="Transfer Receipt",
      description="Transfer receipt",
      is_requiring_verification=False,
    )
    DocumentType.objects.create(
      group="Inventory",
      symbol="MM-",
      is_fixing=False,
      name="Transfer Issue",
      description="Transfer issue",
      is_requiring_verification=False,
    )
    DocumentType.objects.create(
      group="Inventory",
      symbol="N+",
      is_fixing=False,
      name="Inventory Increase",
      description="Inventory increase",
      is_requiring_verification=False,
    )
    DocumentType.objects.create(
      group="Inventory",
      symbol="N-",
      is_fixing=False,
      name="Inventory Decrease",
      description="Inventory decrease",
      is_requiring_verification=False,
    )
    DocumentType.objects.create(
      group="Inventory",
      symbol="PZ",
      is_fixing=False,
      name="Goods Receipt",
      description="Goods receipt",
      is_requiring_verification=False,
    )
    DocumentType.objects.create(
      group="Inventory",
      symbol="PZKOR",
      is_fixing=False,
      name="Goods Receipt Correction",
      description="Goods receipt correction",
      is_requiring_verification=False,
    )
    DocumentType.objects.create(
      group="Inventory",
      symbol="RK",
      is_fixing=False,
      name="Return Receipt",
      description="Return receipt",
      is_requiring_verification=False,
    )
    DocumentType.objects.create(
      group="Inventory",
      symbol="RKW",
      is_fixing=False,
      name="Reserved Stock Correction",
      description="Reserved stock correction",
      is_requiring_verification=False,
    )
    DocumentType.objects.create(
      group="Inventory",
      symbol="RW",
      is_fixing=False,
      name="Return Issue",
      description="Return issue",
      is_requiring_verification=False,
    )
    DocumentType.objects.create(
      group="Inventory",
      symbol="RWKOR",
      is_fixing=False,
      name="Return Issue Correction",
      description="Return issue correction",
      is_requiring_verification=False,
    )
    DocumentType.objects.create(
      group="Inventory",
      symbol="US-",
      is_fixing=False,
      name="Consumption Issue",
      description="Consumption issue",
      is_requiring_verification=False,
    )
    DocumentType.objects.create(
      group="Inventory",
      symbol="US+",
      is_fixing=False,
      name="Consumption Receipt",
      description="Consumption receipt",
      is_requiring_verification=False,
    )
    DocumentType.objects.create(
      group="Inventory",
      symbol="VM-",
      is_fixing=False,
      name="Internal Transfer Issue",
      description="Internal transfer issue",
      is_requiring_verification=False,
    )
    DocumentType.objects.create(
      group="Inventory",
      symbol="VM+",
      is_fixing=False,
      name="Internal Transfer Receipt",
      description="Internal transfer receipt",
      is_requiring_verification=False,
    )
    DocumentType.objects.create(
      group="Inventory",
      symbol="WZ",
      is_fixing=False,
      name="Goods Issue",
      description="Goods issue",
      is_requiring_verification=False,
    )
    DocumentType.objects.create(
      group="Inventory",
      symbol="WZKOR",
      is_fixing=False,
      name="Goods Issue Correction",
      description="Goods issue correction",
      is_requiring_verification=False,
    )
    DocumentType.objects.create(
      group="Inventory",
      symbol="ZAM",
      is_fixing=False,
      name="Online Order Transfer",
      description="Online order transfer",
      is_requiring_verification=False,
    )
    DocumentType.objects.create(
      group="Inventory",
      symbol="ZAMKOR",
      is_fixing=False,
      name="Online Order Transfer Correction",
      description="Online order transfer correction",
      is_requiring_verification=False,
    )
    DocumentType.objects.create(
      group="Inventory",
      symbol="ZWR",
      is_fixing=False,
      name="Return",
      description="Return",
      is_requiring_verification=False,
    )

def delete_initial_document_types(apps, schema_editor):
    DocumentType = apps.get_model('wmsprototype', 'DocumentType')
    DocumentType.objects.filter(symbol__in=["SH", "RC"]).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('wmsprototype', '0007_alter_row_number'),
    ]

    operations = [
        migrations.RunPython(create_initial_document_types, delete_initial_document_types),
    ]
