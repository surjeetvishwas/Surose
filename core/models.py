from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime
import uuid



class User(AbstractUser):
    USER_ROLES = (
        ('manufacturer', 'Manufacturer'),
        ('owner', 'Owner'),
    )
    
    role = models.CharField(max_length=255, choices=USER_ROLES, default='owner', null=True, blank=True)
    stripe_id = models.CharField(max_length=255, null=True, blank=True)
    rooms = models.ManyToManyField('ChatRoom')

    def __str__(self):
        return self.username

    @property
    def is_owner(self):
        return self.role == 'owner'
    
    @property
    def is_manufacturer(self):
        return self.role == 'manufacturer'
    


class Brand(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name
    


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name
    


def product_image_path(instance, filename):
    return f'{instance.__class__.__name__.lower()}/{str(uuid.uuid4())}-{str(datetime.now().timestamp()).replace(".", "")}.{filename.split(".")[-1]}'

class Product(models.Model):
    PRODUCT_STATUSES = (
        ('pending', 'Pending'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )
    PRODUCT_STOCKS = (
        ('in_stock', 'In Stock'),
        ('out_of_stock', 'Out of Stock'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=20, decimal_places=2)
    image = models.ImageField(upload_to=product_image_path)
    stock = models.CharField(max_length=255, choices=PRODUCT_STOCKS, default='in_stock')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    status = models.CharField(max_length=255, choices=PRODUCT_STATUSES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    


class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.comment
    

class ProductOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=255, null=True)
    country = models.CharField(max_length=255, null=True)
    address = models.TextField(null=True)
    state = models.CharField(max_length=255, null=True)
    postcode = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_paid = models.BooleanField(default=False)
    is_shipped = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.user.username
    


class ProductCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(ProductOrder, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.name
    


class ChatRoom(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.message