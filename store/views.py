from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Product, Order, OrderItem
from .forms import RegisterForm
print("STORE VIEWS LOADED")

# ---------------- HOME ----------------
def home(request):
    query = request.GET.get('q')

    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()

    return render(request, 'home.html', {'products': products})


# ---------------- PRODUCT DETAIL ----------------
def product_detail(request, pk):
    product = get_object_or_404(Product, id=pk)
    return render(request, 'product_detail.html', {'product': product})


# ---------------- ADD TO CART ----------------
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})

    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')


# ---------------- CART ----------------
def cart(request):
    cart_data = request.session.get('cart', {})

    cart_items = []
    total = 0

    for product_id, quantity in cart_data.items():
        try:
            product = Product.objects.get(id=int(product_id))

            subtotal = product.price * quantity
            total += subtotal

            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })

        except Product.DoesNotExist:
            continue

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
    })


# ---------------- INCREASE ----------------
def increase_quantity(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] += 1

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')


# ---------------- DECREASE ----------------
def decrease_quantity(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] -= 1

        if cart[product_id] <= 0:
            del cart[product_id]

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')


# ---------------- REMOVE ----------------
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')


# ---------------- CHECKOUT ----------------
def checkout(request):
    cart_data = request.session.get('cart', {})

    cart_items = []
    total = 0

    for product_id, quantity in cart_data.items():
        try:
            product = Product.objects.get(id=int(product_id))

            subtotal = product.price * quantity
            total += subtotal

            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })

        except Product.DoesNotExist:
            continue

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total': total
    })


# ---------------- PLACE ORDER ----------------
@login_required
def place_order(request):
    if request.method != "POST":
        return redirect('cart')

    cart = request.session.get('cart', {})

    if not cart:
        return redirect('cart')

    order = Order.objects.create(
        user=request.user,
        status='confirmed'
    )

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity
            )
        except Product.DoesNotExist:
            continue

    request.session['cart'] = {}
    request.session.modified = True

    return redirect('my_orders')


# ---------------- MY ORDERS ----------------
@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'my_orders.html', {
        'orders': orders
    })


# ---------------- REGISTER ----------------
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})