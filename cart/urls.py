from django.urls import path

from . import views

urlpatterns = [
	path('', views.cart_summary, name='cart-summary'),

	# path('empty/', views.cart_empty, name='cart-empty'),

	path('add/', views.cart_add, name='cart-add'),

	path('delete/', views.cart_delete, name='cart-delete'),

	path('update/', views.cart_update, name='cart-update'),
    #Phúc Tấn 03/11 Thêm các url cần thiết cho trang thanh toán
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('success/', views.success, name='success'),
    path('cancel/', views.cancel, name='cancel'),
    path('pay/', views.pay, name='pay'),
    path('list_successful_payments/', views.list_successful_payments, name='list_successful_payments'),
    path('create-checkout-session/', views.create_checkout_session, name='create-checkout-session'),
    path("payment/", views.payment, name="payment"),
  
]
