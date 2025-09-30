# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ProductTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_class', models.CharField(choices=[('VENTANA', 'Ventana'), ('PUERTA', 'Puerta'), ('ACCESORIO', 'Accesorio')], max_length=20)),
                ('line_name', models.CharField(max_length=50)),
                ('code', models.SlugField(max_length=60, unique=True)),
                ('base_price_net', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('currency', models.CharField(default='ARS', max_length=3)),
                ('requires_dimensions', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=True)),
                ('valid_from', models.DateField(blank=True, null=True)),
                ('valid_to', models.DateField(blank=True, null=True)),
                ('version', models.PositiveIntegerField(default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Plantilla de Producto',
                'verbose_name_plural': 'Plantillas de Producto',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TemplateAttribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60)),
                ('code', models.SlugField(max_length=60)),
                ('type', models.CharField(choices=[('SELECT', 'Select'), ('BOOLEAN', 'Boolean'), ('NUMBER', 'Number'), ('DIMENSIONS_MM', 'Dimensions (mm)'), ('QUANTITY', 'Quantity')], max_length=15)),
                ('is_required', models.BooleanField(default=True)),
                ('order', models.PositiveSmallIntegerField(default=1)),
                ('render_variant', models.CharField(choices=[('select', 'Select'), ('swatches', 'Swatches'), ('radio', 'Radio'), ('buttons', 'Buttons')], default='select', max_length=10)),
                ('rules_json', models.JSONField(blank=True, default=dict)),
                ('min_value', models.DecimalField(blank=True, decimal_places=4, max_digits=12, null=True)),
                ('max_value', models.DecimalField(blank=True, decimal_places=4, max_digits=12, null=True)),
                ('step_value', models.DecimalField(blank=True, decimal_places=4, max_digits=12, null=True)),
                ('unit_label', models.CharField(blank=True, max_length=20)),
                ('min_width', models.PositiveIntegerField(blank=True, null=True)),
                ('max_width', models.PositiveIntegerField(blank=True, null=True)),
                ('min_height', models.PositiveIntegerField(blank=True, null=True)),
                ('max_height', models.PositiveIntegerField(blank=True, null=True)),
                ('step_mm', models.PositiveIntegerField(blank=True, default=10, null=True)),
                ('rebaje_vidrio_mm', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attributes', to='catalog.producttemplate')),
            ],
            options={
                'verbose_name': 'Atributo de Plantilla',
                'verbose_name_plural': 'Atributos de Plantilla',
                'ordering': ['order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='AttributeOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=80)),
                ('code', models.SlugField(max_length=80)),
                ('pricing_mode', models.CharField(choices=[('ABS', 'Suma absoluta por ítem'), ('PER_M2', 'Precio por m²'), ('PERIMETER', 'Precio por perímetro (m)'), ('FACTOR', 'Factor multiplicativo (x)'), ('PER_UNIT', 'Precio por unidad')], default='ABS', max_length=10)),
                ('price_value', models.DecimalField(decimal_places=4, default=0, max_digits=12)),
                ('currency', models.CharField(default='ARS', max_length=3)),
                ('order', models.PositiveSmallIntegerField(default=1)),
                ('is_default', models.BooleanField(default=False)),
                ('swatch_hex', models.CharField(blank=True, max_length=7)),
                ('icon', models.CharField(blank=True, max_length=50)),
                ('qty_attr_code', models.CharField(blank=True, max_length=60)),
                ('attribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='catalog.templateattribute')),
            ],
            options={
                'verbose_name': 'Opción de Atributo',
                'verbose_name_plural': 'Opciones de Atributo',
                'ordering': ['order', 'id'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='templateattribute',
            unique_together={('template', 'code')},
        ),
        migrations.AlterUniqueTogether(
            name='producttemplate',
            unique_together={('line_name', 'version')},
        ),
        migrations.AlterUniqueTogether(
            name='attributeoption',
            unique_together={('attribute', 'code')},
        ),
    ]