from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Cart, CartItem, Order, OrderItem

def get_or_create_cart(request):
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart

def product_list(request):
    categories = Category.objects.all()
    category_id = request.GET.get('category')
    if category_id:
        products = Product.objects.filter(category_id=category_id)
    else:
        products = Product.objects.all()
    return render(request, 'store/product_list.html', {
        'products': products,
        'categories': categories,
        'selected_category': int(category_id) if category_id else None
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})

def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart = get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart')

def cart_view(request):
    cart = get_or_create_cart(request)
    items = cart.items.all()
    return render(request, 'store/cart.html', {'cart': cart, 'items': items})

def remove_from_cart(request, pk):
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, pk=pk, cart=cart)
    cart_item.delete()
    return redirect('cart')

def update_quantity(request, pk):
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, pk=pk, cart=cart)
    quantity = int(request.POST.get('quantity', 1))
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')

def checkout(request):
    cart = get_or_create_cart(request)
    items = cart.items.all()
    if not items:
        return redirect('cart')

    if request.method == 'POST':
        order = Order.objects.create(
            first_name  = request.POST['first_name'],
            last_name   = request.POST['last_name'],
            email       = request.POST['email'],
            address     = request.POST['address'],
            city        = request.POST['city'],
            postal_code = request.POST['postal_code'],
            total       = cart.get_total()
        )
        for item in items:
            OrderItem.objects.create(
                order    = order,
                product  = item.product,
                quantity = item.quantity,
                price    = item.product.price
            )
        cart.items.all().delete()
        return redirect('order_confirmation', pk=order.pk)

    return render(request, 'store/checkout.html', {
        'cart': cart,
        'items': items
    })

def order_confirmation(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'store/order_confirmation.html', {'order': order})