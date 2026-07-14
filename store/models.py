from django.db import models
from django.contrib.auth.models import User


# ---------------- CATEGORY ----------------
class Category(models.Model):

    name = models.CharField(
        max_length=100
    )

    def __str__(self):
        return self.name


# ---------------- PRODUCT ----------------
class Product(models.Model):

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    name = models.CharField(
        max_length=100
    )

    description = models.TextField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True
    )

    stock = models.PositiveIntegerField(
        default=0
    )
    featured = models.BooleanField(
    default=False
)

    def __str__(self):
        return self.name




# ---------------- ORDER ----------------
class Order(models.Model):

    STATUS_CHOICES = (

        ('Pending', 'Pending'),

        ('Confirmed', 'Confirmed'),

        ('Shipped', 'Shipped'),

        ('Delivered', 'Delivered'),

        ('Cancelled', 'Cancelled'),

    )


    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )


    customer_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default=""
    )


    address = models.TextField(
        blank=True,
        null=True,
        default=""
    )


    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        default=""
    )


    payment_method = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default=""
    )


    created_at = models.DateTimeField(
        auto_now_add=True
    )


    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    email = models.EmailField()

    def __str__(self):

        return f"Order #{self.id} - {self.user.username}"



# ---------------- ORDER ITEM ----------------
class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )


    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )


    quantity = models.PositiveIntegerField()


    def __str__(self):

        return f"{self.product.name} x {self.quantity} (Order #{self.order.id})"
   # ---------------- WISHLIST ----------------

class Wishlist(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):

        return f"{self.user.username} - {self.product.name}"



# ---------------- PRODUCT REVIEW ----------------

class Review(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )


    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )


    rating = models.IntegerField(
        choices=[
            (1, '⭐'),
            (2, '⭐⭐'),
            (3, '⭐⭐⭐'),
            (4, '⭐⭐⭐⭐'),
            (5, '⭐⭐⭐⭐⭐'),
        ]
    )


    comment = models.TextField()


    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):

        return f"{self.product.name} - {self.rating}"
    # ---------------- COUPON ----------------

class Coupon(models.Model):

    code = models.CharField(
        max_length=20,
        unique=True
    )

    discount = models.PositiveIntegerField(
        help_text="Discount percentage"
    )

    active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.code