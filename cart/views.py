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

from store.models import Product, ProductDetail, ProductImage, User, Order
from .cart import Cart
from .vnpay import vnpay
import datetime
from ecommerce import settings
import uuid
import json

stripe.api_key = 'sk_test_51QH2duG6ioceCuONjBIvdJJCSr8z7Lo7s0vRd8eDQT0iAZh9i5qpQTbUdKW3RjooRKWwfPbR2a74UIsEb9dQaBfs00PRwhWbI3'
STRIPE_WEBHOOK_SECRET = 'whsec_YJzSC35dyMSepBg5364vlk5aaR0KkBUA'
api_key = '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'
# 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

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
		print("product_id===>",product_id)
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
	email = get_username(request)
	data__ = get_username(request)
	data = data__.content.decode('utf-8')
	json_data = json.loads(data)
	line_items = list_produc(request)
	sum_price = 0
	for i in line_items:
		sum_price += i["price_data"]["unit_amount"]
	send_payment_confirmation_email(api_key, json_data["email"],json_data["name"], "12355")
	create_order(request)
	return render(request, 'cart/success.html', )


def create_order(request):
	print("đã vào đây")
	line_items = list_produc(request)
	sum_price = sum(i["price_data"]["unit_amount"] for i in line_items)  # Tính tổng tiền nhanh hơn
	user_id = request.user.id
	status = "Đang xử lý" 
	total = Decimal(sum_price)  
	shiper = "12/03"  
	user = User.objects.get(id=user_id) 
	order = Order(user_id=user, status=status, total=total, shiper=shiper)
	order.save()
		


def pay(request):
	return render(request, 'cart/pay.html', )


def cancel(request):
	return render(request, 'cart/cancel.html', )


# Đặt secret key của Stripe và webhook secret
endpoint_secret = 'whsec_YJzSC35dyMSepBg5364vlk5aaR0KkBUA'



def get_username(request):
    if request.user.is_authenticated:
       return JsonResponse({
            "name": request.user.last_name,
            "email": request.user.email
        })
    return "Chưa đăng nhập"


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
def send_payment_confirmation_email(api_key, to_email, to_name, amount):
	print("Ddax do day")
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
                    <p><strong>Số tiền:</strong>{amount}</p>
                    <p>Trân trọng,</p>
                    <p>Cảm ơn bạn đã thanh toán đơn hàng</p>
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
		id = item['product'].product_id.id
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
				success_url='http://127.0.0.1:8000/cart/success/',
				cancel_url='http://127.0.0.1:8000/cart/cancel',
				customer_email=request.POST.get('email'),  # Lấy email từ request
				billing_address_collection='required',  # Bắt buộc địa chỉ thanh toán
			)
			return redirect(checkout_session.url)  # Trả về URL của phiên thanh toán
		except stripe.error.StripeError as e:
			return JsonResponse({'error': str(e)})
	return JsonResponse({'error': 'Invalid request'}, status=400)


# thêm công thanh toán với vnPay
@csrf_exempt

def payment(request):
	if request.method == 'POST':
			data__ = get_username(request)
			data = data__.content.decode('utf-8')
			json_data = json.loads(data) 
			print("email====>",json_data)
			line_items = list_produc(request)
			sum_price = 0
			for i in line_items:
				sum_price += i["price_data"]["unit_amount"]
			ipaddr = get_client_ip(request)
			vnp = vnpay()
			vnp.requestData['vnp_Version'] = '2.1.0'
			vnp.requestData['vnp_Command'] = 'pay'
			vnp.requestData['vnp_TmnCode'] = settings.VNPAY_TMN_CODE
			vnp.requestData['vnp_Amount'] = int(sum_price * 100)
			vnp.requestData['vnp_CurrCode'] = 'VND'
			vnp.requestData['vnp_TxnRef'] = str(uuid.uuid4().int)[:10]
			vnp.requestData['vnp_OrderInfo'] = "Nap"
			vnp.requestData['vnp_OrderType'] = "other"
			vnp.requestData['vnp_Locale'] = "vn"
			bank_code = "VNBANK"
			if bank_code:
				vnp.requestData['vnp_BankCode'] = bank_code
			vnp.requestData['vnp_CreateDate'] = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
			vnp.requestData['vnp_IpAddr'] = ipaddr
			vnp.requestData['vnp_ReturnUrl'] = settings.VNPAY_RETURN_URL
			vnpay_payment_url = vnp.get_payment_url(settings.VNPAY_PAYMENT_URL, settings.VNPAY_HASH_SECRET_KEY)
			print(vnpay_payment_url)
				# Redirect to VNPAY
			return redirect(vnpay_payment_url)
	else:
		return render(request, "payment.html", {"title": "Thanh toán"})

 
def vnpay_return(request):
	print("1232313123=======>>>>>")
	vnp = vnpay()
	inputData = request.GET.dict()  # Nhận toàn bộ dữ liệu trả về từ VNPAY
	# Lấy mã kiểm tra (vnp_SecureHash)
	secure_hash = inputData.pop('vnp_SecureHash', None)
	email = get_username(request)
	data__ = get_username(request)
	data = data__.content.decode('utf-8')
	json_data = json.loads(data)
	line_items = list_produc(request)
	sum_price = 0
	for i in line_items:
		sum_price += i["price_data"]["unit_amount"]
	
	print("123434344")
	send_payment_confirmation_email(api_key, json_data["email"],json_data["name"], "12355")
		
	# Kiểm tra chữ ký hợp lệ không?
	if vnp.validate_response(inputData, settings.VNPAY_HASH_SECRET_KEY, secure_hash):
		# Kiểm tra trạng thái giao dịch
		if inputData['vnp_ResponseCode'] == '00':  # Mã '00' = thành công
			return render(request, "cart/success.html", {"message": "Thanh toán thành công!"})
		else:
			return render(request, "payment_fail.html", {"message": "Thanh toán thất bại!"})
	else:
		return HttpResponse("Chữ ký không hợp lệ!", status=400)
            
            


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # Lấy IP đầu tiên trong danh sách
    else:
        ip = request.META.get('REMOTE_ADDR')  # Lấy IP từ request trực tiếp
    return ip
