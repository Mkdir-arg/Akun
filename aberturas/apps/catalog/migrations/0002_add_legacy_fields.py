from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="producttemplate",
            name="legacy_metadata",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="producttemplate",
            name="legacy_product_id",
            field=models.PositiveIntegerField(blank=True, db_index=True, null=True),
        ),
    ]