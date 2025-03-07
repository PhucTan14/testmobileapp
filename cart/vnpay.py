import hashlib
import hmac
import urllib.parse

class vnpay:
    def __init__(self):
        self.requestData = {}

    def get_payment_url(self, vnp_Url, secret_key):
    # Loại bỏ vnp_SecureHash nếu có trong requestData
        data_to_sign = {k: v for k, v in self.requestData.items() if k != "vnp_SecureHash"}

        # Sắp xếp tham số theo thứ tự bảng chữ cái ASCII
        sorted_data = sorted(data_to_sign.items())

        # Tạo query string với mã hóa URL
        query_string = "&".join(f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in sorted_data)

        # In ra để kiểm tra dữ liệu trước khi ký
        print("🔍 Chuỗi dữ liệu trước khi ký:", query_string)

        # Tạo chữ ký SHA512
        signature = hmac.new(secret_key.encode(), query_string.encode(), hashlib.sha512).hexdigest()

        print("🔑 Chữ ký tạo ra:", signature)  # Debug chữ ký

        # Tạo URL thanh toán có chữ ký
        return f"{vnp_Url}?{query_string}&vnp_SecureHash={signature}"