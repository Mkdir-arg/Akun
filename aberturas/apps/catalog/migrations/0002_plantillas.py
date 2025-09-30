# Generated manually for template models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
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
                ('type', models.CharField(choices=[('SELECT', 'Select'), ('BOOLEAN', 'Boolean'), ('NUMBER', 'Number'), ('COLOR', 'Color'), ('MEASURE_MM', 'Measure (mm)')], max_length=15)),
                ('is_required', models.BooleanField(default=True)),
                ('order', models.PositiveSmallIntegerField(default=1)),
                ('rules_json', models.JSONField(blank=True, default=dict)),
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
                ('pricing_mode', models.CharField(choices=[('ABS', 'Suma absoluta por ítem'), ('PER_M2', 'Precio por m²'), ('PERIMETER', 'Precio por perímetro (m)'), ('FACTOR', 'Factor multiplicativo (x)')], default='ABS', max_length=10)),
                ('price_value', models.DecimalField(decimal_places=4, default=0, max_digits=12)),
                ('currency', models.CharField(default='ARS', max_length=3)),
                ('order', models.PositiveSmallIntegerField(default=1)),
                ('is_default', models.BooleanField(default=False)),
                ('attribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='catalog.templateattribute')),
            ],
            options={
                'verbose_name': 'Opción de Atributo',
                'verbose_name_plural': 'Opciones de Atributo',
                'ordering': ['order', 'id'],
            },
        ),
        migrations.AddConstraint(
            model_name='producttemplate',
            constraint=models.UniqueConstraint(fields=('line_name', 'version'), name='catalog_producttemplate_line_name_version_uniq'),
        ),
        migrations.AddConstraint(
            model_name='templateattribute',
            constraint=models.UniqueConstraint(fields=('template', 'code'), name='catalog_templateattribute_template_code_uniq'),
        ),
        migrations.AddConstraint(
            model_name='attributeoption',
            constraint=models.UniqueConstraint(fields=('attribute', 'code'), name='catalog_attributeoption_attribute_code_uniq'),
        ),
    ]