from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [

    # ---------------- HOME ----------------
    path("", views.home, name="home"),

    # ---------------- PRODUCTS ----------------
    path("product/<int:pk>/", views.product_detail, name="product_detail"),
    path("product/<int:product_id>/review/", views.add_review, name="add_review"),

    # ---------------- CART ----------------
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.cart, name="cart"),
    path("increase/<int:product_id>/", views.increase_quantity, name="increase_quantity"),
    path("decrease/<int:product_id>/", views.decrease_quantity, name="decrease_quantity"),
    path("remove/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"),

    # ---------------- CHECKOUT ----------------
    path("checkout/", views.checkout, name="checkout"),
    path("place-order/", views.place_order, name="place_order"),

    # ---------------- ORDERS ----------------
    path("my-orders/", views.my_orders, name="my_orders"),
    path("order/<int:order_id>/", views.order_detail, name="order_detail"),
    path("order/<int:order_id>/invoice/", views.download_invoice, name="download_invoice"),

    # ---------------- AUTH ----------------
    path("register/", views.register, name="register"),

    path(
        "login/",
        auth_views.LoginView.as_view(template_name="login.html"),
        name="login",
    ),

    path("logout/", auth_views.LogoutView.as_view(), name="logout"),


    # ---------------- WISHLIST ----------------
    path("wishlist/", views.wishlist, name="wishlist"),
    path("wishlist/add/<int:product_id>/", views.add_to_wishlist, name="add_to_wishlist"),
    path("wishlist/remove/<int:product_id>/", views.remove_from_wishlist, name="remove_from_wishlist"),


    # ---------------- ADMIN ----------------
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("manage-orders/", views.manage_orders, name="manage_orders"),
    path("update-order/<int:order_id>/", views.update_order_status, name="update_order_status"),


    # ---------------- PAYMENT ----------------
    path("upi-payment/<int:order_id>/", views.upi_payment, name="upi_payment"),
    path("payment-success/", views.payment_success, name="payment_success"),
    path("cancel-order/<int:order_id>/", views.cancel_order, name="cancel_order"),


    # ---------------- TEMP CREATE ADMIN ----------------
    path("create-admin/", views.create_admin, name="create_admin"),

path("create-admin/", views.create_admin, name="create_admin"),
]