from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser


# Create your models here.

class User(AbstractUser):
	email = models.EmailField(unique=True)
	avatar_url = models.URLField(blank=True)
	first_name = models.CharField(max_length=255)
	last_name = models.CharField(max_length=255)
	address = models.TextField(blank=True)
	phone = models.CharField(max_length=20, blank=True)

	def __str__(self):
		return self.username


class Category(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=255, db_index=True)
	slug = models.SlugField(max_length=255, unique=True)

	class Meta:
		verbose_name_plural = 'categories'

	def __str__(self):
		return self.name

	def get_absolute_url(self):
		return reverse('list-category', args=[self.slug])


class Brand(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=255)
	address = models.TextField(blank=True)
	slug = models.SlugField(max_length=255, unique=True)

	class Meta:
		verbose_name_plural = 'brands'

	def __str__(self):
		return self.name

	def get_absolute_url(self):
		return reverse('list-brand', args=[self.slug])


class Product(models.Model):
	id = models.AutoField(primary_key=True)
	category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE,
								 null=True)
	brand = models.ForeignKey(Brand, related_name='products', on_delete=models.CASCADE, null=True)
	title = models.CharField(max_length=255)
	description = models.TextField(blank=True)
	slug = models.SlugField(max_length=255, unique=True)

	class Meta:
		verbose_name_plural = 'products'

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse('product-info', args=[self.slug])


class ProductInfo(models.Model):
	id = models.OneToOneField(Product, primary_key=True, on_delete=models.CASCADE)
	cpu = models.CharField(max_length=255)
	camera = models.CharField(max_length=255)
	battery = models.CharField(max_length=255)
	screen = models.CharField(max_length=255)
	note = models.TextField(blank=True)

	def __str__(self):
		return self.product.title


class ProductDetail(models.Model):
	id = models.AutoField(primary_key=True)
	product_id = models.ForeignKey(Product, related_name='details', on_delete=models.CASCADE)
	color = models.CharField(max_length=255)
	ram = models.CharField(max_length=255)
	storage = models.CharField(max_length=255)
	price = models.DecimalField(max_digits=60, decimal_places=2)
	quantity = models.IntegerField(default=20, null=True)

	def get_formatted_price(self):
		return "{:,.0f} VND".format(self.price)

	def __str__(self):
		return self.product.title


class ProductImage(models.Model):
	id = models.AutoField(primary_key=True)
	product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
	image = models.ImageField(upload_to='images/')
	product_detail_id = models.ForeignKey(ProductDetail, on_delete=models.CASCADE, null=True)

	def __str__(self):
		return self.product.title


class Review(models.Model):
	id = models.AutoField(primary_key=True)
	product_id = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
	user_id = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
	rating = models.IntegerField()
	comment = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.product.title


class Cart(models.Model):
	id = models.AutoField(primary_key=True)
	user_id = models.ForeignKey(User, related_name='carts', on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.user.username


class CartItem(models.Model):
	id = models.AutoField(primary_key=True)
	cart_id = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
	product_detail_id = models.ForeignKey(ProductDetail, related_name='cart_items',
										  on_delete=models.CASCADE)
	quantity = models.IntegerField()

	def __str__(self):
		return self.product.title


class Order(models.Model):
	id = models.AutoField(primary_key=True)
	user_id = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	status = models.CharField(max_length=255)
	total = models.DecimalField(max_digits=60, decimal_places=2)
	shiper = models.CharField(max_length=255)

	def __str__(self):
		return self.user.username


class OrderItem(models.Model):
	id = models.AutoField(primary_key=True)
	order_id = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
	product_detail_id = models.ForeignKey(ProductDetail, related_name='order_items',
										  on_delete=models.CASCADE)
	quantity = models.IntegerField()

	def __str__(self):
		return self.product.title
