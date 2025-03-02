from decimal import Decimal

from store.models import ProductDetail, ProductImage


class Cart:
	def __init__(self, request):
		self.session = request.session

		# return old user cart if exists or create a new one
		cart = self.session.get('session_key')
		if 'session_key' not in request.session:
			cart = self.session['session_key'] = {}
		self.cart = cart

	def add(self, product, product_qty):
		product_id = str(product.id)

		# check if product is already in cart
		if product_id in self.cart:  # if product is already in cart
			self.cart[product_id]['qty'] += product_qty  # modify the quantity
		else:
			self.cart[product_id] = {
				'price': str(product.price),
				'option_text': f"{product.color}, {product.ram}, {product.storage}",
				'qty': product_qty
				}
		self.session.modified = True  # save the session

	def delete(self, product):
		product_id = str(product)
		if product_id in self.cart:
			del self.cart[product_id]
		self.session.modified = True

	def update(self, product, qty):
		product_id = str(product)
		product_quantity = qty
		if product_id in self.cart:
			self.cart[product_id]['qty'] = product_quantity
		self.session.modified = True

	def __len__(self):
		return sum(item['qty'] for item in self.cart.values())  # get total number of items in cart

	def __iter__(self):
		all_products_ids = self.cart.keys()
		products = ProductDetail.objects.filter(id__in=all_products_ids)

		cart = self.cart.copy()

		for product in products:
			thumbnail = ProductImage.objects.filter(product_id=product.product_id).first()
			
			if thumbnail:
				product.thumbnail = thumbnail.image.url
			product.option_text = f"{product.color}, {product.ram}, {product.storage}"
			cart[str(product.id)]['product'] = product

		for item in cart.values():
			item['price'] = Decimal(item['price'])
			item['total'] = item['price'] * item['qty']
			yield item

	def get_total(self):
		total = sum(Decimal(item['price']) * item['qty'] for item in self.cart.values())
		return f"{total:,.0f}₫"
	
