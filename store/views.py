from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Sum, F
from django.contrib.admin.views.decorators import staff_member_required

import io
import base64
import requests

from django.conf import settings
from django.http import HttpResponse
from django.core.mail import send_mail

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from reportlab.pdfgen import canvas

from .models import Product, Order, OrderItem, Category, Wishlist, Review
from .forms import RegisterForm, ReviewForm

print("STORE VIEWS LOADED")

@login_required
def home(request):

    query = request.GET.get('q')
    category_id = request.GET.get('category')

    if query:
        products = Product.objects.filter(
            name__icontains=query
        )

    elif category_id:
        products = Product.objects.filter(
            category_id=category_id
        )

    else:
        products = Product.objects.all()

    # Add average rating to each product
    products = products.annotate(
        average_rating=Avg('review__rating')
    )

    categories = Category.objects.all()

    featured_products = Product.objects.filter(
        featured=True
    ).annotate(
        average_rating=Avg('review__rating')
    )

    return render(
        request,
        'home.html',
        {
            'products': products,
            'categories': categories,
            'featured_products': featured_products,
        }
    )

def product_detail(request, pk):

    product = get_object_or_404(Product, id=pk)

    # ---------------- RECENTLY VIEWED ----------------
    recent = request.session.get('recent_products', [])

    if product.id in recent:
        recent.remove(product.id)

    recent.insert(0, product.id)

    recent = recent[:5]

    request.session['recent_products'] = recent

    # ---------------- REVIEWS ----------------
    reviews = Review.objects.filter(
        product=product
    ).order_by('-created_at')

    average_rating = reviews.aggregate(
        Avg('rating')
    )['rating__avg']

    review_form = ReviewForm()

    # ---------------- RELATED PRODUCTS ----------------
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(
        id=product.id
    )[:4]

    # ---------------- RECENT PRODUCTS ----------------
    recent_products = Product.objects.filter(
        id__in=request.session.get('recent_products', [])
    ).exclude(
        id=product.id
    )
    print(request.session.get('recent_products'))
    return render(
        request,
        'product_detail.html',
        {
            'product': product,
            'reviews': reviews,
            'review_form': review_form,
            'average_rating': average_rating,
            'related_products': related_products,
            'recent_products': recent_products,
        }
    )

# ---------------- ADD TO CART ----------------
def add_to_cart(request, product_id):

    cart = request.session.get('cart', {})

    product_id = str(product_id)

    quantity = int(request.GET.get("quantity", 1))

    if product_id in cart:
        cart[product_id] += quantity
    else:
        cart[product_id] = quantity

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")

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
@login_required
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

def send_whatsapp_message(order):
    url = f"https://graph.facebook.com/v22.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    data = {
        "messaging_product": "whatsapp",
        "to": settings.WHATSAPP_RECIPIENT_NUMBER,
        "type": "text",
        "text": {
            "body": (
                f"🛒 My E-Commerce Store\n\n"
                f"Hello {order.customer_name},\n\n"
                f"Your order #{order.id} has been placed successfully.\n\n"
                f"Payment: {order.payment_method}\n"
                f"Status: {order.status}\n\n"
                f"Thank you for shopping with us!"
            )
        }
    }

    response = requests.post(url, headers=headers, json=data)

    print(response.status_code)
    print(response.text)


def send_order_email(order):

    subject = f"🛒 Order Confirmation - Order #{order.id}"

    message = f"""
Hello {order.customer_name},

==========================================
        MY E-COMMERCE STORE
==========================================

🎉 Thank you for your order!

Your order has been placed successfully.

------------------------------------------
Order Details
------------------------------------------

Order ID       : {order.id}
Customer Name  : {order.customer_name}
Email          : {order.email}
Payment Method : {order.payment_method}
Status         : {order.status}

------------------------------------------

We will notify you once your order is shipped.

Thank you for shopping with us!

Regards,
My E-Commerce Store
"""

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [order.email],
        fail_silently=False,
    )
    print("EMAIL SENT")
@login_required
def place_order(request):

    if request.method != "POST":
        return redirect("cart")

    cart = request.session.get("cart", {})

    if not cart:
        return redirect("cart")

    order = Order.objects.create(
        user=request.user,
        customer_name=request.POST.get("name"),
        email=request.POST.get("email"),
        address=request.POST.get("address"),
        phone=request.POST.get("phone"),
        payment_method=request.POST.get("payment"),
        status="Confirmed"
    )

    products = Product.objects.filter(id__in=cart.keys())
    product_map = {str(product.id): product for product in products}

    for product_id, quantity in cart.items():
        product = product_map.get(str(product_id))
        if product:
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity
            )

    # Clear cart
    request.session["cart"] = {}
    request.session.modified = True

    # Send confirmation email safely
    try:
        send_order_email(order)
        print("Email sent successfully")
    except Exception as e:
        print("Email failed:", e)

    # Clear cart after order
    request.session["cart"] = {}
    request.session.modified = True

    # Redirect to home page

    return redirect("home")
    
# ---------------- MY ORDERS ----------------
@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'my_orders.html', {
        'orders': orders
    })
from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.admin.views.decorators import staff_member_required

# ---------------- ADMIN DASHBOARD ----------------

@staff_member_required
def admin_dashboard(request):

    total_products = Product.objects.count()

    total_orders = Order.objects.count()

    total_customers = Order.objects.values('user').distinct().count()

    total_revenue = 0

    orders = Order.objects.filter(
        status__in=["Confirmed", "confirmed", "Delivered"]
    )

    for order in orders:

        for item in order.orderitem_set.all():

            total_revenue += item.product.price * item.quantity

    recent_orders = Order.objects.order_by('-created_at')[:10]

    # ---------------- SALES CHART ----------------

    labels = []

    sales = []

    for order in orders:

        labels.append(f"Order {order.id}")

        total = 0

        for item in order.orderitem_set.all():

            total += float(item.product.price) * item.quantity

        sales.append(total)

    plt.figure(figsize=(14, 6))

    plt.bar(labels, sales, color="steelblue")

    plt.title("Sales by Order", fontsize=16)

    plt.xlabel("Orders", fontsize=12)

    plt.ylabel("Revenue (₹)", fontsize=12)

    plt.xticks(rotation=60, ha="right", fontsize=8)

    plt.tight_layout(pad=2)

    buffer = io.BytesIO()

    plt.savefig(buffer, format="png")

    buffer.seek(0)

    image_png = buffer.getvalue()

    buffer.close()

    chart = base64.b64encode(image_png).decode("utf-8")

    plt.close()

    top_products = (
        OrderItem.objects
        .values("product__name")
        .annotate(total_sold=Sum("quantity"))
        .order_by("-total_sold")[:5]
    )

    context = {

        "total_products": total_products,

        "total_orders": total_orders,

        "total_customers": total_customers,

        "total_revenue": total_revenue,

        "recent_orders": recent_orders,

        "top_products": top_products,

        "chart": chart,

    }

    return render(
        request,
        "admin_dashboard.html",
        context
    )
# ---------------- ORDER DETAIL ----------------
@login_required
def order_detail(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    total = 0

    for item in order.orderitem_set.all():

        total += item.product.price * item.quantity

    return render(
        request,
        'order_detail.html',
        {
            'order': order,
            'total': total,
        }
    )


from django.contrib.auth import login

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")

    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})
# ---------------- ADD TO WISHLIST ----------------

@login_required
def add_to_wishlist(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    return redirect('wishlist')



# ---------------- REMOVE FROM WISHLIST ----------------

@login_required
def remove_from_wishlist(request, product_id):

    Wishlist.objects.filter(
        user=request.user,
        product_id=product_id
    ).delete()

    return redirect('wishlist')



# ---------------- VIEW WISHLIST ----------------

@login_required
def wishlist(request):

    items = Wishlist.objects.filter(
        user=request.user
    )

    return render(
        request,
        'wishlist.html',
        {
            'items': items
        }
    )
# ---------------- DOWNLOAD INVOICE ----------------
@login_required
def download_invoice(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    response = HttpResponse(content_type='application/pdf')

    response['Content-Disposition'] = (
        f'attachment; filename="invoice_{order.id}.pdf"'
    )

    pdf = canvas.Canvas(response)

    # Store Name
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(200, 800, "MY STORE")

    # Invoice Details
    pdf.setFont("Helvetica", 12)

    pdf.drawString(100, 760, f"Invoice Number : #{order.id}")
    pdf.drawString(100, 740, f"Date : {order.created_at}")

    # Customer Details
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(100, 700, "Customer Details")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 675, f"Name : {order.customer_name}")
    pdf.drawString(100, 655, f"Phone : {order.phone}")
    pdf.drawString(100, 635, f"Address : {order.address}")

    # Products Heading
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(100, 590, "Products")

    # Table Heading
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(100, 565, "Product")
    pdf.drawString(250, 565, "Price")
    pdf.drawString(350, 565, "Qty")
    pdf.drawString(450, 565, "Total")

    y = 540
    total = 0

    pdf.setFont("Helvetica", 12)

    for item in order.orderitem_set.all():

        unit_price = item.product.price
        subtotal = unit_price * item.quantity

        total += subtotal

        pdf.drawString(
            100,
            y,
            item.product.name
        )

        pdf.drawString(
            250,
            y,
            f"₹{unit_price}"
        )

        pdf.drawString(
            350,
            y,
            f"{item.quantity}"
        )

        pdf.drawString(
            450,
            y,
            f"₹{subtotal}"
        )

        y -= 25

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(100, y - 20, f"Total Amount : ₹{total}")

    pdf.drawString(100, y - 50, f"Payment Method : {order.payment_method}")

    pdf.drawString(100, y - 80, f"Order Status : {order.status}")

    pdf.drawString(100, y - 120, "Thank you for shopping with us!")

    pdf.save()

    return response
# ---------------- ADD REVIEW ----------------

@login_required
def add_review(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )


    if request.method == "POST":

        form = ReviewForm(request.POST)


        if form.is_valid():

            review = form.save(commit=False)

            review.product = product

            review.user = request.user

            review.save()

            return redirect(
                'product_detail',
                pk=product.id
            )


    else:

        form = ReviewForm()


    return render(
        request,
        'add_review.html',
        {
            'form': form,
            'product': product
        }
    )



@login_required
def upi_payment(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    total = 0

    for item in order.orderitem_set.all():
        total += item.product.price * item.quantity

    # ADD THIS LINE
    qr_url = "/media/upi_qr.jpeg"

    return render(
        request,
        "upi_payment.html",
        {
            "order": order,
            "total": total,
            "qr_url": qr_url,
        }
    )
    


@login_required
def payment_success(request):
    return render(request, "payment_success.html")


@login_required
def cancel_order(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    # Only allow cancellation if the order is confirmed
    if order.status == "Confirmed":

        # Restore product stock
        for item in order.orderitem_set.all():
            product = item.product
            product.stock += item.quantity
            product.save()

        # Change order status
        order.status = "Cancelled"
        order.save()

        # Optional: Send cancellation email
        # send_cancel_email(order)

    return redirect("order_detail", order_id=order.id)


def send_cancel_email(order):

    subject = f"❌ Order Cancelled - Order #{order.id}"

    message = f"""
Hello {order.customer_name},

Your order has been cancelled successfully.

Order Details
-------------------------

Order ID : {order.id}
Customer : {order.customer_name}
Status   : Cancelled

If this cancellation was accidental,
you can place a new order anytime.

Thank you for shopping with us.

My E-Commerce Store
"""
    send_mail(
    subject,
    message,
    settings.EMAIL_HOST_USER,
    [order.email],
    fail_silently=True,
)


@staff_member_required
def manage_orders(request):

    orders = Order.objects.all().order_by("-created_at")

    return render(
        request,
        "manage_orders.html",
        {
            "orders": orders
        }
    )
@staff_member_required
def update_order_status(request, order_id):

    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        order.status = request.POST.get("status")
        order.save()

    return redirect("manage_orders")

from django.contrib.auth.models import User
from django.http import HttpResponse


def create_admin(request):

    user, created = User.objects.get_or_create(
        username="ram"
    )

    user.set_password("Ram@12345")
    user.email = "rp6961103@gmail.com"
    user.is_superuser = True
    user.is_staff = True
    user.save()

    return HttpResponse("Admin created successfully")