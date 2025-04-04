# Generated manually based on new documentation provided on 2025-04-03
# WARNING: The reverse operation of this migration will delete ALL entries
# in the DocumentType table, not just the ones created here. Use with caution.

from django.db import migrations

def create_updated_document_types(apps, schema_editor):
    """Creates DocumentType instances based on the new documentation."""
    DocumentType = apps.get_model('wmsprototype', 'DocumentType')

    # --- Skladové operácie ---
    DocumentType.objects.create(
        group="Skladové operácie",
        symbol="BO",
        name="Počiatočný stav",
        description="",
        is_for_managers=False,
    )
    DocumentType.objects.create(
        group="Skladové operácie",
        symbol="MM",
        name="Presun v rámci skladu",
        description="",
        is_for_managers=False,
    )
    DocumentType.objects.create(
        group="Skladové operácie",
        symbol="FV",
        name="Expedícia mimo systému",
        description="",
        is_for_managers=False,
    )
    DocumentType.objects.create(
        group="Skladové operácie",
        symbol="IC+",
        name="Výsledok čiastočnej inventúry: úplný prebytok",
        description="",
        is_for_managers=False,
    )
    DocumentType.objects.create(
        group="Skladové operácie",
        symbol="IC-",
        name="Výsledok pĺnej inventúry: manko",
        description="",
        is_for_managers=False,
    )
    DocumentType.objects.create(
        group="Skladové operácie",
        symbol="IP+",
        name="Výsledok pĺnej inventúry: prebytok",
        description="",
        is_for_managers=False,
    )
    DocumentType.objects.create(
        group="Skladové operácie",
        symbol="IP-",
        name="Výsledok pĺnej inventúry: manko",
        description="",
        is_for_managers=False, # Generuje sa automaticky
    )
    DocumentType.objects.create(
        group="Skladové operácie",
        symbol="WM-",
        name="Odpis pre presun",
        description="",
        is_for_managers=False,
    )
    DocumentType.objects.create(
        group="Skladové operácie",
        symbol="WM+",
        name="Príjem po presune",
        description="",
        is_for_managers=False,
    )
    DocumentType.objects.create(
        group="Skladové operácie",
        symbol="NN+",
        name="Neplánovaný príjem",
        description="",
        is_for_managers=False,
    )
    DocumentType.objects.create(
        group="Skladové operácie",
        symbol="NN-",
        name="Neplánovaný výdaj",
        description="",
        is_for_managers=False,
    )
    DocumentType.objects.create(
        group="Skladové operácie",
        symbol="PZ",
        name="Príjem z externého zdroja",
        description="",
        is_for_managers=False,
    )
    DocumentType.objects.create(
        group="Skladové operácie",
        symbol="RW",
        name="Výdaj pred požiadavkou / Predpredajná reklamácia",
        description="",
        is_for_managers=False,
    )
    DocumentType.objects.create(
        group="Skladové operácie",
        symbol="US+",
        name="Korekcia stavu zásob (+)",
        description="",
        is_for_managers=True, # Explicitne uvedené "Len pre manažérov"
    )
    DocumentType.objects.create(
        group="Skladové operácie",
        symbol="US-",
        name="Korekcia stavu zásob (-)",
        description="",
        is_for_managers=True, # Explicitne uvedené "Len pre manažérov"
    )
    DocumentType.objects.create(
        group="Skladové operácie",
        symbol="WZ",
        name="Vrátenie dodávateľovi",
        description="",
        is_for_managers=False, # Storno môže byť len pre manažéra, ale typ ako taký nie
    )
    DocumentType.objects.create(
        group="Skladové operácie",
        symbol="ZB",
        name="Balík zberača (Inventúra)",
        description="",
        is_for_managers=False,
    )

    # --- Externé úlohy ---
    # Poznámka v dokumentácii: "Generovanie a uzatváranie len pre manažérov!"
    DocumentType.objects.create(
        group="Externé úlohy",
        symbol="BMO",
        name="Príkaz na presun v rámci skladu",
        description="",
        is_for_managers=True,
    )
    DocumentType.objects.create(
        group="Externé úlohy",
        symbol="ICO",
        name="Príkaz na úplnú inventúru",
        description="",
        is_for_managers=True,
    )
    DocumentType.objects.create(
        group="Externé úlohy",
        symbol="IPO",
        name="Príkaz na čiastočnú inventúru",
        description="",
        is_for_managers=True,
    )
    DocumentType.objects.create(
        group="Externé úlohy",
        symbol="TRO",
        name="Príkaz na presun medzi skladmi",
        description="",
        is_for_managers=True,
    )
    DocumentType.objects.create(
        group="Externé úlohy",
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
        # Nahraď 'XXXX' skutočným číslom predchádzajúcej migrácie, ak je iné
        ('wmsprototype', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_updated_document_types, delete_all_document_types),
    ]