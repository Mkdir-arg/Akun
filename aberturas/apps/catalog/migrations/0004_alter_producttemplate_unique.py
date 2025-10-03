from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0003_template_categories"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="producttemplate",
            unique_together=set(),
        ),
    ]