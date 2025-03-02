import stripe
# Phúc Tấn 03/11 Thêm các thư viện cần thiết cho thanh toán
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from django.http import JsonResponse, HttpResponse
import os
import requests

from store.models import Product, ProductDetail, ProductImage
from .cart import Cart

stripe.api_key = 'sk_test_51QH2duG6ioceCuONjBIvdJJCSr8z7Lo7s0vRd8eDQT0iAZh9i5qpQTbUdKW3RjooRKWwfPbR2a74UIsEb9dQaBfs00PRwhWbI3'
STRIPE_WEBHOOK_SECRET = 'whsec_YJzSC35dyMSepBg5364vlk5aaR0KkBUA'
api_key = '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'


# acct_1QH2duG6ioceCuON

def cart_summary(request):
	cart = Cart(request)

	return render(request, 'cart/cart-summary.html', {'cart': cart})


def cart_add(request):
	cart = Cart(request)
	if request.POST.get('action') == 'post':
		# product_id = int(request.POST.get('product_id'))
		product_quantity = int(request.POST.get('product_quantity'))
		product_option_id = int(request.POST.get('product_option'))

		product_option = get_object_or_404(ProductDetail, id=product_option_id)
		cart.add(product=product_option, product_qty=product_quantity)
		cart_quantity = cart.__len__()
		response = JsonResponse({'qty': cart_quantity})
		return response


def cart_delete(request):
	cart = Cart(request)
	if request.POST.get('action') == 'post':
		product_id = request.POST.get('product_id')
		cart.delete(product=product_id)
		cart_quantity = cart.__len__()
		cart_total = cart.get_total()
		response = JsonResponse({'qty': cart_quantity, 'total': cart_total})
		return response


def cart_update(request):
	cart = Cart(request)
	if request.POST.get('action') == 'post':
		product_id = request.POST.get('product_id')
		product_quantity = int(request.POST.get('product_quantity'))
		cart.update(product=product_id, qty=product_quantity)
		cart_quantity = cart.__len__()
		cart_total = cart.get_total()
		response = JsonResponse({'qty': cart_quantity, 'total': cart_total})
		return response


# Phúc Tấn Thêm Hàm xử lý thanh toán
def success(request):
	return render(request, 'cart/success.html', )


def cancel(request):
	return render(request, 'cart/cancel.html', )


# Đặt secret key của Stripe và webhook secret
endpoint_secret = 'whsec_YJzSC35dyMSepBg5364vlk5aaR0KkBUA'


@csrf_exempt  # Bỏ qua CSRF verification cho webhook (chỉ dùng cho webhook Stripe)
def stripe_webhook(request):
	if request.method == 'POST':
		payload = request.body
		sig_header = request.META['HTTP_STRIPE_SIGNATURE']
		event = None

		# Kiểm tra chữ ký webhook để đảm bảo tính hợp lệ của yêu cầu
		try:
			event = stripe.Webhook.construct_event(
				payload, sig_header, endpoint_secret  # Thay bằng secret thật của bạn
			)
		except ValueError as e:
			return JsonResponse({'error': f"Invalid payload: {str(e)}"}, status=400)
		except stripe.error.SignatureVerificationError as e:
			return JsonResponse({'error': f"Invalid signature: {str(e)}"}, status=400)

		# Xử lý sự kiện từ Stripe
		if event['type'] == 'charge.updated':
			payment_intent = event['data']['object']
			# Thực hiện hành động xử lý payment_intent
			payment_intent = event['data']['object']
			billing_details = payment_intent['billing_details']
			currency = payment_intent['currency']
			receipt_url = payment_intent['receipt_url']
			amount = payment_intent['amount'] / 100  # Stripe trả về số tiền tính bằng cents
			email = billing_details['email']
			name = billing_details['name']
			transaction_id = payment_intent['id']
			status = payment_intent['status']
			print(amount, email, name, transaction_id, status)
			send_payment_confirmation_email(api_key, email, name, transaction_id, amount, currency,
											receipt_url)
		return JsonResponse({'status': 'success'}, status=200)
	else:
		return JsonResponse({'error': 'Invalid request method'},
							status=405)  # Nếu không phải POST, trả lỗi 405


# Phúc Tấn hàm lấy danh sách sản phẩm đang có trong card
def list_successful_payments(request):
	# Lấy tối đa 1 PaymentIntent
	payment_intents = stripe.PaymentIntent.list(limit=10)
	successful_payments = []

	for intent in payment_intents.data:
		if intent.status == 'succeeded':
			payment_info = {
				'id': intent.id,
				'amount': intent.amount,
				'currency': intent.currency,
				'created': intent.created,
				'email': None,  # Khởi tạo trường email

				# Nếu có, lấy thông tin khách hàng
				'customer': intent.customer,
			}

			# Nếu intent có customer ID, hãy lấy thông tin khách hàng
			if payment_info['customer']:
				customer = stripe.Customer.retrieve(payment_info['customer'])
				payment_info['email'] = customer.email  # Lấy email từ đối tượng Customer

			successful_payments.append(payment_info)

	print(successful_payments)
	return JsonResponse(successful_payments, safe=False)


# Phúc Tấn viết hàm gửi mail cho khách hàng bằng sever mail brevo
def send_payment_confirmation_email(api_key, to_email, to_name, transaction_id, amount, currency,
									receipt_url):
	url = "https://api.brevo.com/v3/smtp/email"
	headers = {
		"accept": "application/json",
		"api-key": api_key,
		"content-type": "application/json"
	}
	data = {
		"sender": {"name": "Công Ty An Toàn Thông Tin Của Tấn",
				   "email": "info@antoanthongtin.online"},
		"to": [{"email": to_email, "name": to_name}],
		"subject": "Xác nhận thanh toán thành công",
		"htmlContent": f"""
            <html>
                <body>
                    <p>Chào {to_name},</p>
                    <p>Cảm ơn bạn đã thanh toán thành công!</p>
                    <p><strong>Mã giao dịch:</strong> {transaction_id}</p>
                    <p><strong>Số tiền:</strong> {amount / 100 if currency.lower() == 'usd' else amount} {currency.upper()}</p>
                    <p><a href="{receipt_url}">Xem biên lai của bạn tại đây</a></p>
                    <p>Trân trọng,</p>
                    <p>An Toan Thong Tin Moi Lam Gui Mail Do Nheng</p>
                </body>
            </html>
        """
	}
	response = requests.post(url, headers=headers, json=data)
	if response.status_code == 201:
		print("Email gửi thành công!")
	else:
		print(f"Lỗi khi gửi email: {response.status_code}, {response.text}")


def list_produc(request):
	cart_instance = Cart(request)
	list_item = []
	for item in cart_instance:
		title = item['product'].product_id.title
		description = item['product'].product_id.description
		list_item.append({
			'price_data': {
				'currency': 'vnd',
				'product_data': {
					'name': title,
					'description': description,
					# Mô tả sản phẩm từ giỏ hàng (nếu có)
				},
				'unit_amount': int(item['price'] * Decimal(1)),  # Giá sản phẩm (cents)
			},
			'quantity': item['qty'],  # Số lượng sản phẩm từ giỏ hàng
		})
	return list_item


@csrf_exempt
def create_checkout_session(request):
	if request.method == 'POST':
		# Không cần lấy từ request.body nữa vì chúng ta sẽ gán cố định và sản phẩm từ trong card ra
		line_items = list_produc(request)
		try:
			# Tạo phiên thanh toán
			checkout_session = stripe.checkout.Session.create(
				payment_method_types=['card'],
				line_items=line_items,
				mode='payment',
				success_url='https://antoanthongtin.online/cart/success/',
				cancel_url='https://antoanthongtin.online/cart/cancel/',
				customer_email=request.POST.get('email'),  # Lấy email từ request
				billing_address_collection='required',  # Bắt buộc địa chỉ thanh toán
			)
			return redirect(checkout_session.url)  # Trả về URL của phiên thanh toán
		except stripe.error.StripeError as e:
			return JsonResponse({'error': str(e)})
	return JsonResponse({'error': 'Invalid request'}, status=400)
