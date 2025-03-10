# Generated by Django 5.1.2 on 2024-11-07 04:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0002_brand_productinfo_remove_product_brand_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="brand",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="products",
                to="store.brand",
            ),
        ),
    ]
