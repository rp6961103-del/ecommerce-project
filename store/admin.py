from django.contrib import admin
from .models import Category, Product, Order, OrderItem, Wishlist, Review, Coupon


admin.site.register(Coupon)


# ---------------- CATEGORY ADMIN ----------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
    )

    search_fields = (
        'name',
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'category',
        'price',
        'stock',
        'featured',
    )

    list_filter = (
        'category',
        'featured',
    )

    search_fields = (
        'name',
    )

    list_editable = (
        'featured',
    )
# ---------------- ORDER ITEM INLINE ----------------

class OrderItemInline(admin.TabularInline):

    model = OrderItem

    extra = 0


# ---------------- ORDER ADMIN ----------------

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'customer_name',
        'phone',
        'payment_method',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'payment_method',
        'created_at',
    )

    search_fields = (
        'customer_name',
        'phone',
        'user__username',
    )

    inlines = [
        OrderItemInline
    ]


# ---------------- WISHLIST ADMIN ----------------

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'product',
        'created_at',
    )

    search_fields = (
        'user__username',
        'product__name',
    )


# ---------------- REVIEW ADMIN ----------------

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_display = (
        'product',
        'user',
        'rating',
        'created_at',
    )

    list_filter = (
        'rating',
    )

    search_fields = (
        'product__name',
        'user__username',
    )