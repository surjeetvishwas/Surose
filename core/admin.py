from django.contrib import admin
from .models import User, Brand, Category, Product, ProductOrder, ProductCart, ChatRoom, ChatMessage



admin.site.register(User)
admin.site.register(Brand)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductOrder)
admin.site.register(ProductCart)
admin.site.register(ChatRoom)
admin.site.register(ChatMessage)