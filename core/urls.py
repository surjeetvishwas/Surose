from django.urls import path
from . import views

app_name = 'core'
urlpatterns = [
    path('login-register/', views.login_register, name='login_register'),
    path('logout/', views.auth_logout, name='auth_logout'),

    path('product/cart/', views.product_cart, name='product_cart'),
    path('product/cart/add/<product_id>/', views.product_cart_add, name='product_cart_add'),
    path('product/cart/delete/<cart_id>/', views.product_cart_delete, name='product_cart_delete'),

    path('product/checkout/', views.product_checkout, name='product_checkout'),

    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('products/', views.products, name='products'),
    path('products/<page>/', views.products, name='products'),
    path('product/review/create/<product_id>/', views.product_review_create, name='product_review_create'),
    path('product/<product_slug>/', views.product_detail, name='product_detail'),

    path('account/users/', views.account_user_list, name='account_user_list'),
    path('account/user/edit/<user_id>/', views.account_user_edit, name='account_user_edit'),
    path('account/user/delete/<user_id>/', views.account_user_delete, name='account_user_delete'),
    path('account/user/role/edit/<user_id>/<action>/', views.account_user_role_edit, name='account_user_role_edit'),
    path('account/orders/', views.account_order_list, name='account_order_list'),
    path('account/order/payment/', views.account_order_payment, name='account_order_payment'),
    path('account/order/payment/return/', views.account_order_payment_return, name='account_order_payment_return'),
    path('account/order/<order_id>/', views.account_order_detail, name='account_order_detail'),
    path('account/order/shipped/<order_id>/', views.account_order_shipped, name='account_order_shipped'),
    path('account/bulk/order/list/', views.account_bulk_order_list, name='account_bulk_order_list'),
    path('account/bulk/order/list/<manufacturer_username>/', views.account_bulk_order_list, name='account_bulk_order_list'),
    path('account/products/', views.account_product_list, name='account_product_list'),
    path('account/product/create/', views.account_product_create, name='account_product_create'),
    path('account/product/edit/<product_id>/', views.account_product_edit, name='account_product_edit'),
    path('account/product/delete/<product_id>/', views.account_product_delete, name='account_product_delete'),
    path('account/product/status/edit/<product_id>/<action>/', views.account_product_status_edit, name='account_product_status_edit'),
    path('account/profile/', views.account_profile, name='account_profile'),
    path('account/payout/', views.account_payout, name='account_payout'),
    path('account/messages/', views.account_message_list, name='account_message_list'),
    path('account/message/<username>/', views.account_message_detail, name='account_message_detail'),
]