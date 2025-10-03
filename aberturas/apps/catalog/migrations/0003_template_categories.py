from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0002_add_legacy_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="TemplateCategory",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("legacy_extrusora_id", models.PositiveIntegerField(db_index=True)),
                ("legacy_extrusora_name", models.CharField(blank=True, max_length=150)),
                ("name", models.CharField(max_length=120)),
                ("slug", models.SlugField(max_length=150, unique=True)),
                ("description", models.CharField(blank=True, max_length=200)),
                ("order", models.PositiveIntegerField(default=0)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["order", "name"],
                "verbose_name": "Categoria de Plantilla",
                "verbose_name_plural": "Categorias de Plantillas",
            },
        ),
        migrations.AddField(
            model_name="producttemplate",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="templates",
                to="catalog.templatecategory",
            ),
        ),
        migrations.AddField(
            model_name="producttemplate",
            name="legacy_extrusora_id",
            field=models.PositiveIntegerField(blank=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name="producttemplate",
            name="legacy_extrusora_name",
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name="templateattribute",
            name="legacy_payload",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="attributeoption",
            name="legacy_payload",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
