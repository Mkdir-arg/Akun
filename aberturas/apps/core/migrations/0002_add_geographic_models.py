# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Provincia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Provincia',
                'verbose_name_plural': 'Provincias',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Municipio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('provincia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='municipios', to='core.provincia')),
            ],
            options={
                'verbose_name': 'Municipio',
                'verbose_name_plural': 'Municipios',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Localidad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('municipio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='localidades', to='core.municipio')),
            ],
            options={
                'verbose_name': 'Localidad',
                'verbose_name_plural': 'Localidades',
                'ordering': ['nombre'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='municipio',
            unique_together={('nombre', 'provincia')},
        ),
        migrations.AlterUniqueTogether(
            name='localidad',
            unique_together={('nombre', 'municipio')},
        ),
    ]