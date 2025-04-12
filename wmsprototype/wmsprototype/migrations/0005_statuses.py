from django.db import migrations, models

def create_statuses(apps, schema_editor):
    # We need to get the historical models as they were at the point of this migration
    Status = apps.get_model('wmsprototype', 'Status')
    DocumentType = apps.get_model('wmsprototype', 'DocumentType')
    
    # FVO statuses
    fvo = DocumentType.objects.get(symbol='FVO')
    Status.objects.create(document_type=fvo, name='Generated')
    Status.objects.create(document_type=fvo, name='In Progress')
    Status.objects.create(document_type=fvo, name='Prepared')
    Status.objects.create(document_type=fvo, name='Completed')
    Status.objects.create(document_type=fvo, name='Canceled')

    # ICO statuses
    ico = DocumentType.objects.get(symbol='ICO')
    Status.objects.create(document_type=ico, name='Generated')
    Status.objects.create(document_type=ico, name='In Progress')
    Status.objects.create(document_type=ico, name='Completed')
    Status.objects.create(document_type=ico, name='Canceled')

    # IPO statuses
    ipo = DocumentType.objects.get(symbol='IPO')
    Status.objects.create(document_type=ipo, name='Generated')
    Status.objects.create(document_type=ipo, name='In Progress')
    Status.objects.create(document_type=ipo, name='Completed')
    Status.objects.create(document_type=ipo, name='Canceled')

    # MMO statuses
    mmo = DocumentType.objects.get(symbol='MMO')
    Status.objects.create(document_type=mmo, name='Generated')
    Status.objects.create(document_type=mmo, name='In Progress')
    Status.objects.create(document_type=mmo, name='Completed')
    Status.objects.create(document_type=mmo, name='Canceled')

    # TRO statuses
    tro = DocumentType.objects.get(symbol='TRO')
    Status.objects.create(document_type=tro, name='Generated')
    Status.objects.create(document_type=tro, name='In Progress')
    Status.objects.create(document_type=tro, name='Prepared')
    Status.objects.create(document_type=tro, name='Completed')
    Status.objects.create(document_type=tro, name='Canceled')


class Migration(migrations.Migration):

    dependencies = [
        ('wmsprototype', '0004_final_polyshing')
    ]

    operations = [
        migrations.RunPython(create_statuses),
    ]

    