from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from core.models import Product, ProductCart, ProductOrder, ChatMessage, ChatRoom
from django.shortcuts import get_object_or_404
from django.db.models import F, Sum
from django.template.defaultfilters import floatformat
from core.decorators import only_in



# start: General
@api_view(['POST'])
@only_in(['owner'])
def product_cart_quantity_update(request):
    cart_id = request.data.get('cart_id')
    quantity = request.data.get('quantity')
    if not cart_id or not quantity:
        return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)
    cart = get_object_or_404(ProductCart, id=cart_id, order=None)
    try:
        quantity = int(quantity)
    except ValueError:
        return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)
    cart.quantity = quantity
    cart.save()
    total_cart = ProductCart.objects.filter(user=request.user, order=None).annotate(total=F('quantity') * F('product__price')).aggregate(Sum('total'))['total__sum']
    return Response({
        'success': 'Cart updated', 
        'quantity': cart.quantity,
        'total': floatformat(cart.quantity * cart.product.price, 2),
        'total_cart': floatformat(total_cart, 2) if total_cart else '0.00',
    }, status=status.HTTP_200_OK)
# end: General



# start: Chat
@api_view(['POST'])
def chat_message_create(request):
    message = request.data.get('message')
    room = request.data.get('room')
    product_id = request.data.get('product_id', None)
    product = get_object_or_404(Product, id=product_id) if product_id else None
    if not message or not room:
        return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)
    if not message:
        return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)
    room = get_object_or_404(ChatRoom, id=room)
    chat = ChatMessage.objects.create(user=request.user, message=message, room=room, product=product)
    return Response({
        'status': 'success',
        'chat': {
            'id': chat.id
        }
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
def chat_message_read(request):
    room = request.data.get('room')
    chat_id = request.data.get('chat_id')
    chat = None
    if not room:
        return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)
    room = get_object_or_404(ChatRoom, id=room)
    if chat_id:
        chat = get_object_or_404(ChatMessage, room=room, id=chat_id, is_read=False)
        chat.is_read = True
        chat.save()
    else:
        room.chatmessage_set.exclude(user=request.user).filter(is_read=False).update(is_read=True)
    return Response({'status': 'success'}, status=status.HTTP_200_OK)
# end: Chat