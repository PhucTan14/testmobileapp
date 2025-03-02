from django.shortcuts import get_object_or_404
from django.shortcuts import render

from .models import Category, Product, ProductImage, ProductDetail


def error_404(request, exception):
	return render(request, 'store/404.html')


def error_500(request):
	return render(request, 'store/500.html')


def info(request):
	print(request.user.is_authenticated)
	return {'user': request.user}


# Create your views here.
def login(request):
	return render(request, 'store/login.html')


def store(request):
	all_products = Product.objects.all()
	for product in all_products:
		product.price = ProductDetail.objects.filter(
			product_id=product.id).first().get_formatted_price()
		product.thumbnail = ProductImage.objects.filter(product_id=product.id).first().image
	return render(request, 'store/store.html', context={'all_products': all_products})


def categories(request):
	all_categories = Category.objects.all()
	return {'all_categories': all_categories}


def list_category(request, category_slug=None):
	category = get_object_or_404(Category, slug=category_slug)
	products = Product.objects.filter(category=category)
	for product in products:
		product.price = ProductDetail.objects.filter(
			product_id=product.id).first().get_formatted_price()
		product.thumbnail = ProductImage.objects.filter(product_id=product.id).first().image
	return render(request, 'store/list-category.html',
				  context={'category': category, 'products': products})


def product_info(request, slug):
	product = get_object_or_404(Product, slug=slug)
	product.images = ProductImage.objects.filter(product_id=product.id).all()
	product.options = ProductDetail.objects.filter(product_id=product.id).all()
	for option in product.options:
		option.price = option.get_formatted_price()
	return render(request, 'store/product-info.html', context={'product': product})


def profile(request):
	return render(request, 'store/profile.html')
