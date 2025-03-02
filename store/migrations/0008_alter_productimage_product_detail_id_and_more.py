# Generated by Django 5.1.2 on 2024-11-08 03:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0007_productimage_product_detail_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="productimage",
            name="product_detail_id",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="store.productdetail",
            ),
        ),
        migrations.AlterField(
            model_name="productimage",
            name="product_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="store.product"
            ),
        ),
    ]
