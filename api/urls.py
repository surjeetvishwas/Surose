from django.urls import path
from . import views

app_name = 'api'
urlpatterns = [
    path('product/cart/quantity/update/', views.product_cart_quantity_update, name='product_cart_quantity_update'),

    path('chat/message/create/', views.chat_message_create, name='chat_message_create'),
    path('chat/message/read/', views.chat_message_read, name='chat_message_read'),
]