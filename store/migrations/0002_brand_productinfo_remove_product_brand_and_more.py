# Generated by Django 5.1.2 on 2024-11-07 04:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Brand",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=255)),
                ("address", models.TextField(blank=True)),
                ("slug", models.SlugField(max_length=255, unique=True)),
            ],
            options={
                "verbose_name_plural": "brands",
            },
        ),
        migrations.CreateModel(
            name="ProductInfo",
            fields=[
                (
                    "id",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to="store.product",
                    ),
                ),
                ("cpu", models.CharField(max_length=255)),
                ("camera", models.CharField(max_length=255)),
                ("battery", models.CharField(max_length=255)),
                ("screen", models.CharField(max_length=255)),
                ("note", models.TextField(blank=True)),
            ],
        ),
        migrations.RemoveField(
            model_name="product",
            name="brand",
        ),
        migrations.RemoveField(
            model_name="product",
            name="image",
        ),
        migrations.RemoveField(
            model_name="product",
            name="price",
        ),
        migrations.AlterField(
            model_name="category",
            name="id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="product",
            name="id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.CreateModel(
            name="Cart",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="carts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("status", models.CharField(max_length=255)),
                ("total", models.DecimalField(decimal_places=2, max_digits=60)),
                ("shiper", models.CharField(max_length=255)),
                (
                    "user_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="orders",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ProductDetail",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("color", models.CharField(max_length=255)),
                ("ram", models.CharField(max_length=255)),
                ("storage", models.CharField(max_length=255)),
                ("price", models.DecimalField(decimal_places=2, max_digits=60)),
                ("quantity", models.IntegerField()),
                (
                    "product_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="details",
                        to="store.product",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("quantity", models.IntegerField()),
                (
                    "order_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="store.order",
                    ),
                ),
                (
                    "product_detail_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="order_items",
                        to="store.productdetail",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CartItem",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("quantity", models.IntegerField()),
                (
                    "cart_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="store.cart",
                    ),
                ),
                (
                    "product_detail_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cart_items",
                        to="store.productdetail",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ProductImage",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("image", models.ImageField(upload_to="images/")),
                (
                    "product_detail_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="images",
                        to="store.productdetail",
                    ),
                ),
                (
                    "product_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="images",
                        to="store.product",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Review",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("rating", models.IntegerField()),
                ("comment", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "product_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to="store.product",
                    ),
                ),
                (
                    "user_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
