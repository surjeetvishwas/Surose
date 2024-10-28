from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from django.contrib.auth.decorators import login_required
from .decorators import only_anonymous, only_admin, only_in
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.db.models import Q, Avg, Sum, F, Prefetch
from .models import Brand, Category, Product, ProductReview, ProductCart, ProductOrder, ChatRoom, ChatMessage
from django.core.paginator import Paginator
from django.conf import settings
from django.utils.text import slugify
import urllib
import json
from utils.stripe import create_account, create_account_link, delete_account, retrieve_account, create_payment, retrieve_payment


User = get_user_model()

# start: Authentication
@only_anonymous
def login_register(request):
    next = request.GET.get('next')
    if request.method == 'POST':
        if 'register' in request.POST:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            agree = request.POST.get('agree')
            manufacturer = request.POST.get('manufacturer')
            if not username:
                messages.error(request, 'Username is required.')
            elif not email:
                messages.error(request, 'Email is required.')
            elif not password:
                messages.error(request, 'Password is required.')
            elif not agree:
                messages.error(request, 'You must agree to the terms first.')
            if not agree or not username or not email or not password:
                return redirect('core:login_register')
            if User.objects.filter(Q(username=username) | Q(email=email)).exists():
                messages.error(request, 'Username or email is taken.')
                return redirect('core:login_register')
            user = User.objects.create_user(username=username, email=email, password=password)
            user.is_active = False
            if manufacturer:
                user.role = 'manufacturer'
            user.save()
            messages.success(request, 'Account created successfully. Please wait for approval.')
            return redirect('core:login_register')
        elif 'login' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')
            if not username:
                messages.error(request, 'Username is required.')
            elif not password:
                messages.error(request, 'Password is required.')
            if not username or not password:
                return redirect('core:login_register')
            if not User.objects.filter(username=username).exists():
                messages.error(request, 'Account does not exist.')
                return redirect('core:login_register')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if not user.is_active:
                    messages.error(request, 'Account is not active.')
                    return redirect('core:login_register')
                login(request, user)
                return redirect(next) if next else redirect('core:home')
            else:
                messages.error(request, 'Invalid credentials.')
                return redirect('core:login_register')
    return render(request, 'authentication/login-register.html')

def auth_logout(request):
    logout(request)
    return redirect('core:login_register')
# end: Authentication

# start: General
def home(request):
    products = Product.objects.filter(status='published').annotate(rating_avg=Avg('productreview__rating', default=0))
    context = {
        'products': {
            'popular': products.order_by('?')[:8],
            'new': products.order_by('-created_at')[:8],
            'hero': products.order_by('-created_at')[:4],
        }
    }
    return render(request, 'home.html', context=context)

def products(request, page=None):
    search = request.GET.get('search', '')
    category = request.GET.get('category')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    filter = Q(name__icontains=search) | Q(description__icontains=search) | Q(brand__name__icontains=search) | Q(category__name__icontains=search)
    if category:
        filter &= Q(category__slug=category)
    if price_min:
        try:
            price_min = float(price_min)
            if price_min < 0:
                messages.error(request, 'Price min must be greater than or equal to 0.')
                return redirect('core:products')
            filter &= Q(price__gte=price_min)
        except:
            messages.error(request, 'Price min must be a number.')
            return redirect('core:products')
    if price_max:
        try:
            price_max = float(price_max)
            if price_max < 0:
                messages.error(request, 'Price max must be greater than or equal to 0.')
                return redirect('core:products')
            filter &= Q(price__lte=price_max)
        except:
            messages.error(request, 'Price max must be a number.')
            return redirect('core:products')
    products_paginator = Paginator(Product.objects.annotate(rating_avg=Avg('productreview__rating', default=0)).filter(status='published').filter(filter).order_by('-created_at'), 10)
    products = products_paginator.get_page(page)
    context = {
        'products': {
            'list': products,
            'popular': Product.objects.filter(status='published').order_by('?')[:8],
        },
        'categories': Category.objects.all(),
        'brands': Brand.objects.all(),
        'params': '?'+urllib.parse.urlencode(request.GET) if search else ''
    }
    return render(request, 'products.html', context=context)

def product_detail(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug, status='published')
    rating_avg = product.productreview_set.aggregate(Avg('rating', default=0))['rating__avg']
    context = {
        'product': product,
        'rating_avg': rating_avg,
        'categories': Category.objects.all()[:6],
        'products': {
            'popular': Product.objects.filter(status='published').exclude(id=product.id).order_by('?')[:8],
            'similar': Product.objects.filter(status='published').annotate(rating_avg=Avg('productreview__rating', default=0)).filter(category=product.category).exclude(id=product.id)[:8],
        },
        'reviews': ProductReview.objects.select_related('user').filter(product=product).order_by('-created_at')
    }
    return render(request, 'product-detail.html', context=context)

@login_required
@only_in(['owner'])
def product_review_create(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        if not rating or not comment:
            messages.error(request, 'All fields are required.')
            return redirect('core:product_detail', product_slug=product.slug)
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                messages.error(request, 'Rating must be between 1 and 5.')
                return redirect('core:product_detail', product_slug=product.slug)
        except:
            messages.error(request, 'Rating must be a number.')
            return redirect('core:product_detail', product_slug=product.slug)
        ProductReview.objects.create(
            user=request.user,
            product=product,
            rating=rating,
            comment=comment
        )
        messages.success(request, 'Review created successfully.')
    return redirect('core:product_detail', product_slug=product.slug)

@login_required
@only_in(['owner'])
def product_cart(request):
    context = {
        'carts': ProductCart.objects.select_related('product').filter(user=request.user, order=None).annotate(total=F('quantity') * F('product__price')).order_by('-created_at'),
        'total': ProductCart.objects.filter(user=request.user, order=None).annotate(total=F('quantity') * F('product__price')).aggregate(Sum('total'))['total__sum']
    }
    return render(request, 'product-cart.html', context=context)

@login_required
@only_in(['owner'])
def product_cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    next = request.GET.get('next')
    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        if not quantity:
            messages.error(request, 'Quantity is required.')
            return redirect(next) if next else redirect('core:product_detail', product_slug=product.slug)
        try:
            quantity = int(quantity)
            if quantity < 1:
                messages.error(request, 'Quantity must be greater than or equal to 1.')
                return redirect(next) if next else redirect('core:product_detail', product_slug=product.slug)
        except:
            messages.error(request, 'Quantity must be a number.')
            return redirect(next) if next else redirect('core:product_detail', product_slug=product.slug)
        if product.stock == 'out_of_stock':
            messages.error(request, 'Product is out of stock.')
            return redirect(next) if next else redirect('core:product_detail', product_slug=product.slug)
        if ProductCart.objects.filter(user=request.user, product=product, order=None).exists():
            messages.error(request, 'Product already in cart.')
            return redirect(next) if next else redirect('core:product_detail', product_slug=product.slug)
        if ProductCart.objects.filter(user=request.user, order=None).exists():
            product_cart = ProductCart.objects.filter(user=request.user, order=None).first()
            if product_cart.product.user != product.user:
                messages.error(request, 'You can only add products from the same manufacturer.')
                return redirect(next) if next else redirect('core:product_detail', product_slug=product.slug)
        ProductCart.objects.create(
            user=request.user,
            product=product,
            quantity=quantity
        )
        messages.success(request, 'Product added to cart successfully.')
        if next:
            return redirect(next)
    return redirect('core:product_detail', product_slug=product.slug)

@login_required
@only_in(['owner'])
def product_cart_delete(request, cart_id):
    cart = get_object_or_404(ProductCart, id=cart_id)
    cart.delete()
    messages.success(request, 'Product deleted from cart successfully.')
    return redirect('core:product_cart')

@login_required
@only_in(['owner'])
def product_checkout(request):
    carts = ProductCart.objects.select_related('product').filter(user=request.user, order=None).annotate(total=F('quantity') * F('product__price')).order_by('-created_at')
    subtotal = ProductCart.objects.filter(user=request.user, order=None).annotate(total=F('quantity') * F('product__price')).aggregate(Sum('total'))['total__sum']
    if not carts:
        messages.error(request, 'Cart is empty.')
        return redirect('core:product_cart')
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        country = request.POST.get('country')
        address = request.POST.get('address')
        state = request.POST.get('state')
        postcode = request.POST.get('postcode')
        terms = request.POST.get('checkout-terms')
        if not first_name or not last_name or not email or not country or not address or not state or not postcode:
            messages.error(request, 'Please fill all required fields.')
            return redirect('core:product_checkout')
        if not terms:
            messages.error(request, 'You must agree to the terms first.')
            return redirect('core:product_checkout')
        product_order = ProductOrder.objects.create(
            user=request.user,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            country=country,
            address=address,
            state=state,
            postcode=postcode,
        )
        carts.update(order=product_order)
        messages.success(request, 'Checkout success.')
        return redirect('core:account_order_list')
    with open('static/assets/json/countries.json') as f:
        countries = json.load(f)
    context = {
        'carts': carts,
        'subtotal': subtotal,
        'total': subtotal + settings.SHIPPING_CHARGE,
        'ship_charge': settings.SHIPPING_CHARGE,
        'countries': countries
    }
    return render(request, 'product-checkout.html', context=context)

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')
# end: General

# start: Account
@login_required
@only_admin
def account_user_list(request):
    context = {
        'users': User.objects.exclude(id=request.user.id).order_by('-date_joined'),
    }
    return render(request, 'account/user/list.html', context=context)

@login_required
@only_admin
def account_user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        admin = request.POST.get('admin')
        if not username or not email:
            messages.error(request, 'All fields are required.')
            return redirect('core:account_user_edit')
        user.username = username
        user.email = email
        user.is_superuser = admin is not None
        user.save()
        messages.success(request, 'User updated successfully.')
        return redirect('core:account_user_list')
    context = {
        'user_item': user,
    }
    return render(request, 'account/user/edit.html', context=context)

@login_required
@only_admin
def account_user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, 'User deleted successfully.')
    return redirect('core:account_user_list')

@login_required
@only_admin
def account_user_role_edit(request, user_id, action):
    user = get_object_or_404(User, id=user_id)
    if action == 'accept':
        user.is_active = True
        user.save()
    else:
        user.delete()
    messages.success(request, 'User role updated successfully.')
    return redirect('core:account_user_list')

@login_required
@only_in(['admin', 'manufacturer'])
def account_product_list(request):
    product_filter = Q(user=request.user)
    if request.user.is_superuser:
        product_filter = Q()
    context = {
        'products': Product.objects.filter(product_filter).select_related('category', 'brand', 'user').order_by('-created_at')
    }
    return render(request, 'account/product/list.html', context=context)

@login_required
@only_in(['admin', 'manufacturer'])
def account_product_create(request):
    account = retrieve_account(request.user.stripe_id)
    if not account['charges_enabled']:
        messages.error(request, 'You must connect your account first.')
        return redirect('core:account_payout')
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        image = request.FILES.get('image')
        stock = request.POST.get('stock')
        brand = request.POST.get('brand')
        brand_slug = slugify(brand)
        category = request.POST.get('category')
        category_slug = slugify(category)
        description = request.POST.get('description')
        if not name or not price or not image or not brand or not stock or not category or not description:
            messages.error(request, 'All fields are required.')
            return redirect('core:account_product_create')
        try:
            price = float(price)
            if price < 0:
                messages.error(request, 'Price must be greater than or equal to 0.')
                return redirect('core:account_product_create')
        except:
            messages.error(request, 'Price must be a number.')
            return redirect('core:account_product_create')
        if Brand.objects.filter(slug=brand_slug).exists():
            brand = get_object_or_404(Brand, slug=brand_slug)
        else:
            brand = Brand.objects.create(name=brand, slug=brand_slug)
        if Category.objects.filter(slug=category_slug).exists():
            category = get_object_or_404(Category, slug=category_slug)
        else:
            category = Category.objects.create(name=category, slug=category_slug)
        Product.objects.create(
            user=request.user,
            name=name,
            price=price,
            image=image,
            brand=brand,
            stock=stock,
            category=category,
            description=description
        )
        messages.success(request, 'Product created successfully.')
        return redirect('core:account_product_list')
    context = {
        'stocks': Product.PRODUCT_STOCKS,
    }
    return render(request, 'account/product/create.html', context)

@login_required
@only_in(['admin', 'manufacturer'])
def account_product_edit(request, product_id):
    account = retrieve_account(request.user.stripe_id)
    if not account['charges_enabled']:
        messages.error(request, 'You must connect your account first.')
        return redirect('core:account_payout')
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        image = request.FILES.get('image')
        stock = request.POST.get('stock')
        brand = request.POST.get('brand')
        brand_slug = slugify(brand)
        category = request.POST.get('category')
        category_slug = slugify(category)
        description = request.POST.get('description')
        if not name or not price or not brand or not stock or not category or not description:
            messages.error(request, 'All fields are required.')
            return redirect('core:account_product_edit')
        try:
            price = float(price)
            if price < 0:
                messages.error(request, 'Price must be greater than or equal to 0.')
                return redirect('core:account_product_edit')
        except:
            messages.error(request, 'Price must be a number.')
            return redirect('core:account_product_edit')
        if not request.user.is_superuser and product.user != request.user:
            messages.error(request, 'You are not allowed to edit this product.')
            return redirect('core:account_product_list')
        if Brand.objects.filter(slug=brand_slug).exists():
            brand = get_object_or_404(Brand, slug=brand_slug)
        else:
            brand = Brand.objects.create(name=brand, slug=brand_slug)
        if Category.objects.filter(slug=category_slug).exists():
            category = get_object_or_404(Category, slug=category_slug)
        else:
            category = Category.objects.create(name=category, slug=category_slug)
        product.name = name
        product.price = price
        if image:
            product.image = image
        product.stock = stock
        product.brand = brand
        product.category = category
        product.description = description
        if product.status == 'archived':
            product.status = 'pending'
        product.save()
        messages.success(request, 'Product updated successfully.')
        return redirect('core:account_product_list')
    context = {
        'product': product,
        'stocks': Product.PRODUCT_STOCKS,
    }
    return render(request, 'account/product/edit.html', context=context)

@login_required
@only_in(['admin', 'manufacturer'])
def account_product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if product.user != request.user:
        messages.error(request, 'You are not allowed to delete this product.')
        return redirect('core:account_product_list')
    product.delete()
    messages.success(request, 'Product deleted successfully.')
    return redirect('core:account_product_list')

@login_required
@only_admin
def account_product_status_edit(request, product_id, action):
    product = get_object_or_404(Product, id=product_id)
    if action == 'accept':
        product.status = 'published'
        product.save()
        messages.success(request, 'Product published successfully.')
    elif action == 'reject':
        product.status = 'archived'
        product.save()
        messages.success(request, 'Product archived successfully.')
    return redirect('core:account_product_list')

@login_required
def account_profile(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm-password')
        if not username or not email or not password or not confirm:
            messages.error(request, 'All fields are required.')
            return redirect('core:account_profile')
        if password != confirm:
            messages.error(request, 'Passwords do not match.')
            return redirect('core:account_profile')
        request.user.username = username
        request.user.email = email
        request.user.set_password(password)
        request.user.save()
        user = authenticate(request, username=username, password=password)
        login(request, user)
        messages.success(request, 'Profile updated successfully.')
        return redirect('core:account_profile')
    return render(request, 'account/profile.html')

@login_required
def account_order_list(request):
    orders_filter = Q(user=request.user)
    if request.user.is_superuser:
        orders_filter = Q()
    else:
        if request.user.is_manufacturer:
            orders_filter = Q(user=request.user) | Q(productcart__product__user=request.user)
    context = {
        'orders': ProductOrder.objects.filter(orders_filter).annotate(total=Sum(F('productcart__quantity') * F('productcart__product__price'))).order_by('-created_at')
    }
    return render(request, 'account/order/list.html', context=context)

@login_required
def account_order_detail(request, order_id):
    order = get_object_or_404(ProductOrder, id=order_id)
    total = order.productcart_set.annotate(total=F('quantity') * F('product__price')).aggregate(Sum('total'))['total__sum']
    context = {
        'order': order,
        'carts': order.productcart_set.select_related('product').annotate(total=F('quantity') * F('product__price')).order_by('-created_at'),
        'total': total,
    }
    return render(request, 'account/order/detail.html', context=context)

@login_required
@only_in(['owner'])
def account_order_payment(request):
    if request.method == 'POST':
        order_id = request.POST.get('order-id')
        order = get_object_or_404(ProductOrder, id=order_id)
        seller = order.productcart_set.first().product.user
        payment = create_payment(seller.stripe_id, [{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': x.product.name,
                },
                'unit_amount': int(x.product.price) * 100,
            },
            'quantity': x.quantity,
        } for x in order.productcart_set.all()], settings.SHIPPING_CHARGE, request.build_absolute_uri(resolve_url('core:account_order_payment_return'))+'?session_id={CHECKOUT_SESSION_ID}&order_id='+order_id)
        context = {
            'payment_secret': payment.client_secret,
            'stripe_key': settings.STRIPE_PUBLISH_KEY
        }
        return render(request, 'account/order/payment.html', context)
    return redirect('core:account_order_list')

@login_required
@only_in(['owner'])
def account_order_payment_return(request):
    order_id = request.GET.get('order_id')
    order = get_object_or_404(ProductOrder, id=order_id)
    session_id = request.GET.get('session_id')
    payment = retrieve_payment(session_id)
    if payment['status'] == 'complete':
        order.is_paid = True
        order.payment_id = payment['id']
        order.save()
    return redirect('core:account_order_detail', order_id=order_id)

@login_required
@only_in(['admin', 'manufacturer'])
def account_order_shipped(request, order_id):
    order = get_object_or_404(ProductOrder, id=order_id)
    order.is_shipped = not order.is_shipped
    order.save()
    messages.success(request, 'Order updated successfully.')
    return redirect('core:account_order_list')

@login_required
@only_in(['owner'])
def account_bulk_order_list(request, manufacturer_username=None):
    if request.method == 'POST':
        if 'add-bulk-cart' in request.POST:
            carts = request.POST.getlist('add-to-cart')
            product_carts = request.user.productcart_set.filter(order=None)
            product_user = None
            if product_carts.exists():
                product_user = product_carts.first().product.user
            try:
                for cart in carts:
                    product = get_object_or_404(Product, id=cart, status='published', user=product_user) if product_user else get_object_or_404(Product, id=cart, status='published')
                    qty = int(request.POST.get(f'qty-{cart}'))
                    product_carts = request.user.productcart_set.filter(product=product, order=None)
                    if product_carts.exists():
                        product_cart = product_carts.first()
                        product_cart.quantity += qty
                        product_cart.save()
                    else:
                        ProductCart.objects.create(
                            user=request.user,
                            product=product,
                            quantity=qty
                        )
                messages.success(request, 'Products added to cart successfully.')
            except:
                messages.error(request, 'Something went wrong.')
        manufacturer = request.POST.get('manufacturer') or manufacturer_username
        return redirect('core:account_bulk_order_list', manufacturer_username=manufacturer) if manufacturer else redirect('core:account_bulk_order_list')
    context = {
        'manufacturers': User.objects.filter(role='manufacturer', is_superuser=False)
    }
    if manufacturer_username:
        manufacturer = get_object_or_404(User, username=manufacturer_username)
        products = Product.objects.filter(status='published', user=manufacturer).order_by('-created_at')
        context['products'] = products
        context['manufacturer'] = manufacturer
    return render(request, 'account/bulk-order/list.html', context=context)

@login_required
@only_in(['manufacturer'])
def account_payout(request):
    context = {}
    if request.method == 'POST':
        if not request.user.stripe_id:
            account = create_account(request.user.email)
            if not account:
                messages.error(request, 'Something went wrong.')
                return redirect('core:account_payout')
            request.user.stripe_id = account['id']
            request.user.save()
        link = create_account_link(request.user.stripe_id, request.build_absolute_uri())
        if not link:
            messages.error(request, 'Something went wrong.')
            return redirect('core:account_payout')
        return redirect(link['url'])
    if request.user.stripe_id:
        account = retrieve_account(request.user.stripe_id)
        context['connected'] = account['charges_enabled']
    return render(request, 'account/payout/connect.html', context)

@login_required
@only_in(['owner', 'manufacturer'])
def account_message_list(request):
    rooms = []
    for room in request.user.rooms.prefetch_related('user_set').all():
        room.user1 = room.user_set.exclude(id=request.user.id).first()
        room.unread = room.chatmessage_set.exclude(user=request.user).filter(is_read=False).count()
        rooms.append(room)
    context = {
        'rooms': rooms
    }
    return render(request, 'account/message/list.html', context)

@login_required
@only_in(['owner', 'manufacturer'])
def account_message_detail(request, username):
    user1 = get_object_or_404(User, username=username)
    if user1 == request.user:
        return redirect('core:account_message_list')
    room_check = ChatRoom.objects.filter(user=request.user).filter(user=user1).prefetch_related(Prefetch('chatmessage_set', queryset=ChatMessage.objects.select_related('user', 'product')))
    room = None
    if room_check.exists():
        room = room_check.first()
    else:
        room = ChatRoom.objects.create()
        room.user_set.set([request.user, user1])
    manufacturer = request.user if request.user.is_manufacturer else user1
    context = {
        'room': room,
        'user1': user1,
        'products': manufacturer.product_set.filter(status='published').order_by('-created_at')
    }
    return render(request, 'account/message/detail.html', context)
# end: Account