from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CheckoutForm, LoginForm, RegisterForm
from .models import Cart, CartItem, Category, Order, OrderItem, Product


def home(request):
    products = Product.objects.select_related("category").all()
    categories = Category.objects.all()

    return render(
        request,
        "store/home.html",
        {
            "products": products,
            "categories": categories,
        },
    )


def product_list(request):
    products = Product.objects.select_related("category").all()
    categories = Category.objects.all()

    search = request.GET.get("search", "").strip()
    category_id = request.GET.get("category", "").strip()
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()

    if search:
        products = products.filter(
            Q(name__icontains=search)
            | Q(description__icontains=search)
        )

    if category_id:
        products = products.filter(category_id=category_id)

    if min_price:
        try:
            products = products.filter(
                price__gte=Decimal(min_price)
            )
        except (ValueError, ArithmeticError):
            pass

    if max_price:
        try:
            products = products.filter(
                price__lte=Decimal(max_price)
            )
        except (ValueError, ArithmeticError):
            pass

    return render(
        request,
        "store/products.html",
        {
            "products": products,
            "categories": categories,
            "search": search,
            "selected_category": category_id,
            "min_price": min_price,
            "max_price": max_price,
        },
    )


def product_detail(request, product_id):
    product = get_object_or_404(
        Product.objects.select_related("category"),
        id=product_id,
    )

    related_products = (
        Product.objects.filter(category=product.category)
        .exclude(id=product.id)
        .select_related("category")[:4]
    )

    return render(
        request,
        "store/product_detail.html",
        {
            "product": product,
            "related_products": related_products,
        },
    )


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            messages.success(
                request,
                "Account created successfully. Welcome!",
            )

            return redirect("home")
    else:
        form = RegisterForm()

    return render(
        request,
        "store/register.html",
        {"form": form},
    )


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            messages.success(
                request,
                "You have logged in successfully.",
            )

            next_url = request.GET.get("next")

            if next_url:
                return redirect(next_url)

            return redirect("home")
    else:
        form = LoginForm()

    return render(
        request,
        "store/login.html",
        {"form": form},
    )


@login_required
def logout_view(request):
    logout(request)

    messages.success(
        request,
        "You have been logged out.",
    )

    return redirect("home")


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
    )

    if request.method != "POST":
        return redirect(
            "product_detail",
            product_id=product.id,
        )

    if product.stock <= 0:
        messages.error(
            request,
            "This product is currently out of stock.",
        )

        return redirect(
            "product_detail",
            product_id=product.id,
        )

    cart, _ = Cart.objects.get_or_create(
        user=request.user
    )

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={"quantity": 1},
    )

    if not created:

        if cart_item.quantity >= product.stock:
            messages.warning(
                request,
                "You cannot add more than the available stock.",
            )

            return redirect("cart")

        cart_item.quantity += 1
        cart_item.save()

    messages.success(
        request,
        f"{product.name} added to your cart.",
    )

    return redirect("cart")


@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(
        user=request.user
    )

    items = cart.items.select_related(
        "product",
        "product__category",
    )

    total = sum(
        (item.subtotal for item in items),
        Decimal("0.00"),
    )

    return render(
        request,
        "store/cart.html",
        {
            "cart": cart,
            "items": items,
            "total": total,
        },
    )


@login_required
def update_cart(request, item_id):
    item = get_object_or_404(
        CartItem.objects.select_related(
            "product",
            "cart",
        ),
        id=item_id,
        cart__user=request.user,
    )

    if request.method != "POST":
        return redirect("cart")

    try:
        quantity = int(
            request.POST.get(
                "quantity",
                1,
            )
        )

    except (ValueError, TypeError):
        messages.error(
            request,
            "Invalid quantity.",
        )

        return redirect("cart")

    if quantity < 1:
        item.delete()

        messages.success(
            request,
            "Item removed from your cart.",
        )

        return redirect("cart")

    if quantity > item.product.stock:
        messages.error(
            request,
            f"Only {item.product.stock} item(s) are available.",
        )

        return redirect("cart")

    item.quantity = quantity
    item.save()

    messages.success(
        request,
        "Cart updated successfully.",
    )

    return redirect("cart")


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user,
    )

    if request.method == "POST":
        item.delete()

        messages.success(
            request,
            "Item removed from your cart.",
        )

    return redirect("cart")


@login_required
def checkout(request):
    cart, _ = Cart.objects.get_or_create(
        user=request.user
    )

    items = list(
        cart.items.select_related("product")
    )

    if not items:
        messages.warning(
            request,
            "Your cart is empty.",
        )

        return redirect("products")

    total = sum(
        (item.subtotal for item in items),
        Decimal("0.00"),
    )

    if request.method == "POST":
        form = CheckoutForm(request.POST)

        if form.is_valid():

            try:
                with transaction.atomic():

                    for item in items:

                        product = Product.objects.select_for_update().get(
                            id=item.product.id
                        )

                        if product.stock < item.quantity:
                            raise ValueError(
                                f"Insufficient stock for {product.name}."
                            )

                    order = Order.objects.create(
                        user=request.user,
                        total_amount=total,
                        shipping_address=form.cleaned_data[
                            "shipping_address"
                        ],
                    )

                    for item in items:

                        product = Product.objects.select_for_update().get(
                            id=item.product.id
                        )

                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=item.quantity,
                            price=product.price,
                        )

                        product.stock -= item.quantity

                        product.save(
                            update_fields=["stock"]
                        )

                    cart.items.all().delete()

                messages.success(
                    request,
                    f"Order #{order.id} placed successfully.",
                )

                return redirect(
                    "order_detail",
                    order_id=order.id,
                )

            except ValueError as error:

                messages.error(
                    request,
                    str(error),
                )

                return redirect("cart")

    else:
        form = CheckoutForm()

    return render(
        request,
        "store/checkout.html",
        {
            "form": form,
            "items": items,
            "total": total,
        },
    )


@login_required
def my_orders(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .prefetch_related("items__product")
        .order_by("-created_at")
    )

    return render(
        request,
        "store/orders.html",
        {
            "orders": orders,
        },
    )


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product"),
        id=order_id,
        user=request.user,
    )

    return render(
        request,
        "store/order_detail.html",
        {
            "order": order,
        },
    )


@login_required
def profile(request):
    return render(
        request,
        "store/profile.html",
        {
            "user": request.user,
        },
    )


@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(
            request,
            "You do not have permission to access the admin dashboard.",
        )

        return redirect("home")

    total_products = Product.objects.count()

    total_customers = User.objects.filter(
        is_staff=False,
        is_superuser=False,
    ).count()

    total_orders = Order.objects.count()

    total_revenue = (
        Order.objects
        .exclude(status="Cancelled")
        .aggregate(total=Sum("total_amount"))
        ["total"]
        or Decimal("0.00")
    )

    pending_orders = Order.objects.filter(
        status="Pending"
    ).count()

    recent_orders = (
        Order.objects
        .select_related("user")
        .prefetch_related("items__product")
        .order_by("-created_at")[:10]
    )

    return render(
        request,
        "store/admin_dashboard.html",
        {
            "total_products": total_products,
            "total_customers": total_customers,
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "pending_orders": pending_orders,
            "recent_orders": recent_orders,
        },
    )


@login_required
def update_order_status(request, order_id):
    if not request.user.is_staff:
        messages.error(
            request,
            "You do not have permission to update order status.",
        )
        return redirect("home")

    if request.method != "POST":
        return redirect("admin_dashboard")

    order = get_object_or_404(
        Order,
        id=order_id,
    )

    new_status = request.POST.get("status", "").strip()

    valid_statuses = dict(Order.STATUS_CHOICES)

    if new_status not in valid_statuses:
        messages.error(
            request,
            "Invalid order status.",
        )
        return redirect("admin_dashboard")

    order.status = new_status
    order.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    messages.success(
        request,
        f"Order #{order.id} status updated to {order.status}.",
    )

    return redirect("admin_dashboard")