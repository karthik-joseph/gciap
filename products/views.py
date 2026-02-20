from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Cart, CartItem, Order, OrderItem
from .forms import ProductForm

def product_list(request):
    products = Product.objects.all()
    category = request.GET.get('category', '')
    budget   = request.GET.get('budget', '')

    if category:
        products = products.filter(category=category)
    if budget:
        products = products.filter(budget_level=budget)

    category_labels = {
        'furniture':             'Furniture',
        'decor':                 'Decor',
        'construction_material': 'Construction Materials',
    }
    budget_labels = {
        'low':    'Low Budget',
        'medium': 'Medium Budget',
        'high':   'High Budget',
    }

    selected_category_label = category_labels.get(category, '')
    selected_budget_label   = budget_labels.get(budget, '')

    return render(request, 'products/product_list.html', {
        'products':               products,
        'selected_category_label': selected_category_label,
        'selected_budget_label':   selected_budget_label,
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/product_detail.html', {'product': product})

@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f'{product.name} added to cart!')
    return redirect('products:product_list')

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    total = cart.get_total()
    return render(request, 'products/cart.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required
def update_cart_item(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
    return redirect('products:cart_view')

@login_required
def remove_from_cart(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart!')
    return redirect('products:cart_view')

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()
    if not cart_items:
        messages.error(request, 'Your cart is empty!')
        return redirect('products:cart_view')
    
    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address')
        total = cart.get_total()
        order = Order.objects.create(
            user=request.user,
            total_amount=total,
            shipping_address=shipping_address
        )
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
        cart_items.delete()
        messages.success(request, f'Order #{order.id} placed successfully!')
        return redirect('users:booking_history')
    
    total = cart.get_total()
    return render(request, 'products/checkout.html', {
        'cart_items': cart_items,
        'total': total
    })
