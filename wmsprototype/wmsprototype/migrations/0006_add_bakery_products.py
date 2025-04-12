from django.db import migrations
from decimal import Decimal

def add_bakery_products(apps, schema_editor):
    """
    Add 20 sample bakery products to the database.
    """
    Product = apps.get_model('wmsprototype', 'Product')
    
    bakery_products = [
        {
            'name': 'Rožok Pivec',
            'unit_price': Decimal('0.59'),
            'weight': 59,
            'ean': '590339845123',
            'scu': 'PEC-S-ROZ-PIV',
            'description': 'Classic white bread roll'
        },
        {
            'name': 'Bageta Francúzska',
            'unit_price': Decimal('1.29'),
            'weight': 250,
            'ean': '590339845124',
            'scu': 'PEC-B-FRA',
            'description': 'Traditional French baguette'
        },
        {
            'name': 'Chlieb Kváskový',
            'unit_price': Decimal('3.49'),
            'weight': 500,
            'ean': '590339845125',
            'scu': 'PEC-C-KVA',
            'description': 'Artisan sourdough bread'
        },
        {
            'name': 'Croissant Maslový',
            'unit_price': Decimal('1.49'),
            'weight': 85,
            'ean': '590339845126',
            'scu': 'PEC-C-MAS',
            'description': 'Butter croissant'
        },
        {
            'name': 'Rohlík Celozrnný',
            'unit_price': Decimal('0.79'),
            'weight': 65,
            'ean': '590339845127',
            'scu': 'PEC-R-CEL',
            'description': 'Whole grain roll'
        },
        {
            'name': 'Vianočka Tradičná',
            'unit_price': Decimal('2.99'),
            'weight': 400,
            'ean': '590339845128',
            'scu': 'PEC-V-TRA',
            'description': 'Traditional sweet braided bread'
        },
        {
            'name': 'Štrúdľa Jablková',
            'unit_price': Decimal('2.49'),
            'weight': 300,
            'ean': '590339845129',
            'scu': 'PEC-S-JAB',
            'description': 'Apple strudel'
        },
        {
            'name': 'Koláč Tvarohový',
            'unit_price': Decimal('1.89'),
            'weight': 120,
            'ean': '590339845130',
            'scu': 'PEC-K-TVA',
            'description': 'Cottage cheese pastry'
        },
        {
            'name': 'Buchta Maková',
            'unit_price': Decimal('1.69'),
            'weight': 110,
            'ean': '590339845131',
            'scu': 'PEC-B-MAK',
            'description': 'Poppy seed bun'
        },
        {
            'name': 'Chlieb Ražný',
            'unit_price': Decimal('2.99'),
            'weight': 450,
            'ean': '590339845132',
            'scu': 'PEC-C-RAZ',
            'description': 'Rye bread'
        },
        {
            'name': 'Muffin Čokoládový',
            'unit_price': Decimal('1.29'),
            'weight': 90,
            'ean': '590339845133',
            'scu': 'PEC-M-COK',
            'description': 'Chocolate muffin'
        },
        {
            'name': 'Donut Glazovaný',
            'unit_price': Decimal('1.39'),
            'weight': 75,
            'ean': '590339845134',
            'scu': 'PEC-D-GLA',
            'description': 'Glazed donut'
        },
        {
            'name': 'Bábovka Citrónová',
            'unit_price': Decimal('3.49'),
            'weight': 380,
            'ean': '590339845135',
            'scu': 'PEC-B-CIT',
            'description': 'Lemon bundt cake'
        },
        {
            'name': 'Pletenka Slaná',
            'unit_price': Decimal('1.19'),
            'weight': 95,
            'ean': '590339845136',
            'scu': 'PEC-P-SLA',
            'description': 'Salty braided pastry'
        },
        {
            'name': 'Pizza Rohlík',
            'unit_price': Decimal('1.59'),
            'weight': 110,
            'ean': '590339845137',
            'scu': 'PEC-P-ROH',
            'description': 'Pizza flavored roll'
        },
        {
            'name': 'Žemľa Grahamová',
            'unit_price': Decimal('0.69'),
            'weight': 60,
            'ean': '590339845138',
            'scu': 'PEC-Z-GRA',
            'description': 'Graham flour bun'
        },
        {
            'name': 'Pagáč Oškvarkový',
            'unit_price': Decimal('1.29'),
            'weight': 85,
            'ean': '590339845139',
            'scu': 'PEC-P-OSK',
            'description': 'Crackling scone'
        },
        {
            'name': 'Chlieb Bezlepkový',
            'unit_price': Decimal('4.99'),
            'weight': 350,
            'ean': '590339845140',
            'scu': 'PEC-C-BEZ',
            'description': 'Gluten-free bread'
        },
        {
            'name': 'Moravský Koláč',
            'unit_price': Decimal('2.29'),
            'weight': 130,
            'ean': '590339845141',
            'scu': 'PEC-M-KOL',
            'description': 'Moravian wedding cake'
        },
        {
            'name': 'Perník Medový',
            'unit_price': Decimal('2.99'),
            'weight': 200,
            'ean': '590339845142',
            'scu': 'PEC-P-MED',
            'description': 'Honey gingerbread'
        }
    ]
    
    for product_data in bakery_products:
        Product.objects.create(**product_data)
    
def remove_bakery_products(apps, schema_editor):
    """
    Remove the bakery products added by this migration.
    """
    Product = apps.get_model('wmsprototype', 'Product')
    
    # Get all EANs from the bakery products list
    product_eans = [
        '590339845123', '590339845124', '590339845125', '590339845126', '590339845127',
        '590339845128', '590339845129', '590339845130', '590339845131', '590339845132',
        '590339845133', '590339845134', '590339845135', '590339845136', '590339845137',
        '590339845138', '590339845139', '590339845140', '590339845141', '590339845142'
    ]
    
    # Delete all products with these EANs
    Product.objects.filter(ean__in=product_eans).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('wmsprototype', '0005_statuses'),
    ]

    operations = [
        migrations.RunPython(add_bakery_products, remove_bakery_products),
    ]
