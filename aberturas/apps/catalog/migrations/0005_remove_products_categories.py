# Generated manually to remove products and categories

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0004_attributeoption_icon_attributeoption_qty_attr_code_and_more'),
    ]

    operations = [
        # Eliminar tablas relacionadas con productos y categorías
        migrations.RunSQL("DROP TABLE IF EXISTS catalog_reglaListaprecios CASCADE;"),
        migrations.RunSQL("DROP TABLE IF EXISTS catalog_listaprecios CASCADE;"),
        migrations.RunSQL("DROP TABLE IF EXISTS catalog_producto CASCADE;"),
        migrations.RunSQL("DROP TABLE IF EXISTS catalog_subcategoriaproducto CASCADE;"),
        migrations.RunSQL("DROP TABLE IF EXISTS catalog_categoriaproducto CASCADE;"),
        migrations.RunSQL("DROP TABLE IF EXISTS catalog_tasaimpuesto CASCADE;"),
        migrations.RunSQL("DROP TABLE IF EXISTS catalog_colorproducto CASCADE;"),
        migrations.RunSQL("DROP TABLE IF EXISTS catalog_lineaproducto CASCADE;"),
        migrations.RunSQL("DROP TABLE IF EXISTS catalog_medidaproducto CASCADE;"),
        migrations.RunSQL("DROP TABLE IF EXISTS catalog_unidadmedida CASCADE;"),
    ]