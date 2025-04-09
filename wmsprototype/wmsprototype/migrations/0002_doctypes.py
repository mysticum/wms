from django.db import migrations

def create_updated_document_types(apps, schema_editor):
    """Creates DocumentType instances based on the new documentation."""
    DocumentType = apps.get_model('wmsprototype', 'DocumentType')

    # --- Sklád ---
    DocumentType.objects.create(
        group="Sklád",
        symbol="BO",
        name="Počiatočný stav",
        description="",
        is_for_managers=True,
    )
    DocumentType.objects.create(
        group="Sklád",
        symbol="MM",
        name="Presun v rámci skladu",
        description="",
        is_for_managers=False,
    )
    DocumentType.objects.create(
        group="Sklád",
        symbol="FV",
        name="Expedícia mimo systému",
        description="",
        is_for_managers=False,
    )
    DocumentType.objects.create(
        group="Sklád",
        symbol="IC+",
        name="Výsledok čiastočnej inventúry: úplný prebytok",
        description="",
        is_for_managers=False,
    )
    DocumentType.objects.create(
        group="Sklád",
        symbol="IC-",
        name="Výsledok pĺnej inventúry: manko",
        description="",
        is_for_managers=False,
    )
    DocumentType.objects.create(
        group="Sklád",
        symbol="IP+",
        name="Výsledok pĺnej inventúry: prebytok",
        description="",
        is_for_managers=False,
    )
    DocumentType.objects.create(
        group="Sklád",
        symbol="IP-",
        name="Výsledok pĺnej inventúry: manko",
        description="",
        is_for_managers=False, # Generuje sa automaticky
    )
    DocumentType.objects.create(
        group="Sklád",
        symbol="WM-",
        name="Odpis pre presun",
        description="",
        is_for_managers=False,
    )
    DocumentType.objects.create(
        group="Sklád",
        symbol="WM+",
        name="Príjem po presune",
        description="",
        is_for_managers=False,
    )
    DocumentType.objects.create(
        group="Sklád",
        symbol="NN+",
        name="Neplánovaný príjem",
        description="",
        is_for_managers=False,
    )
    DocumentType.objects.create(
        group="Sklád",
        symbol="NN-",
        name="Neplánovaný výdaj",
        description="",
        is_for_managers=False,
    )
    DocumentType.objects.create(
        group="Sklád",
        symbol="PZ",
        name="Príjem z externého zdroja",
        description="",
        is_for_managers=False,
    )
    DocumentType.objects.create(
        group="Sklád",
        symbol="RW-",
        name="Výdaj pred požiadavkou / Predpredajná reklamácia",
        description="",
        is_for_managers=False,
    )
    DocumentType.objects.create(
        group="Sklád",
        symbol="ZB",
        name="Balík zberača (Inventúra)",
        description="",
        is_for_managers=False,
    )

    # --- Úlohy ---
    DocumentType.objects.create(
        group="Úlohy",
        symbol="BMO",
        name="Príkaz na presun v rámci skladu",
        description="",
        is_for_managers=True,
    )
    DocumentType.objects.create(
        group="Úlohy",
        symbol="ICO",
        name="Príkaz na úplnú inventúru",
        description="",
        is_for_managers=True,
    )
    DocumentType.objects.create(
        group="Úlohy",
        symbol="IPO",
        name="Príkaz na čiastočnú inventúru",
        description="",
        is_for_managers=True,
    )
    DocumentType.objects.create(
        group="Úlohy",
        symbol="TRO",
        name="Príkaz na presun medzi skladmi",
        description="",
        is_for_managers=True,
    )
    DocumentType.objects.create(
        group="Úlohy",
        symbol="FVO",
        name="Príkaz na expedíciu mimo systému",
        description="",
        is_for_managers=True,
    )


def delete_all_document_types(apps, schema_editor):
    """
    Deletes ALL DocumentType instances currently in the database.
    WARNING: This is generally unsafe for reversible migrations as it may
    delete data not created by the forward operation.
    """
    DocumentType = apps.get_model('wmsprototype', 'DocumentType')
    DocumentType.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('wmsprototype', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_updated_document_types, delete_all_document_types),
    ]