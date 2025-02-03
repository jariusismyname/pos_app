from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import LoginForm, SignUpForm, ProductForm
from .models import Product, CustomUser, Cart, CartItem, Order
from django.contrib.auth.decorators import login_required


# Delete product view
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, "Product deleted successfully!")
    return redirect('crud')  # Redirect to the CRUD page after deletion


# Edit product view
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect('crud')  # Redirect to the CRUD page after successful update
    else:
        form = ProductForm(instance=product)

    return render(request, 'edit_product.html', {'form': form, 'product': product})

from django.contrib import messages
from django.shortcuts import render, redirect

def custom_admin_login(request):
    # Clear any old messages when visiting the admin login page
    storage = messages.get_messages(request)
    storage.used = True  # This clears all previous messages

    if request.method == 'POST':
        password = request.POST.get('password')
        if password == "password":
            return redirect('crud')  # Redirect to CRUD page if password is correct
        else:
            messages.error(request, "Incorrect password!")  # Show error only if wrong password

    return render(request, 'admin_login.html')  # Show admin login page

# Welcome Page
def welcome(request):
    return render(request, 'welcome.html')


# Login View
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            try:
                user = CustomUser.objects.get(username=form.cleaned_data['username'])
            except CustomUser.DoesNotExist:
                messages.error(request, "User does not exist")
                return render(request, 'login.html', {'form': form})

            if user.check_password(form.cleaned_data['password']):
                login(request, user)
                return redirect('products')  # Redirect to the products page for regular users
            else:
                messages.error(request, "Incorrect password")
                return render(request, 'login.html', {'form': form})

    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


# Sign Up View
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_customer = True
            user.save()
            login(request, user)
            return redirect('products')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


# Products View (with cart data)
def products_view(request):
    products = Product.objects.filter(quantity__gt=0)

    # Get or create the cart for the logged-in user
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Render the products page with the cart information
    return render(request, 'products.html', {'products': products, 'cart': cart})


from django.shortcuts import render, get_object_or_404
from .models import Cart

def view_cart(request):
    # Get the user's cart
    cart = get_object_or_404(Cart, user=request.user)
    
    # Get all the items in the cart
    cart_items = cart.items.all()

    # Render the cart page with the cart items
    return render(request, 'cart.html', {'cart': cart, 'cart_items': cart_items})
from django.shortcuts import get_object_or_404, redirect
from .models import Cart, CartItem, Product
from django.contrib import messages

# Add product to cart
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Get or create the cart for the logged-in user
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Check if the product is already in the cart
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1  # Increase the quantity if product already in cart
    cart_item.save()

    messages.success(request, f"{product.name} added to your cart.")
    return redirect('products')  # Redirect back to the products page


# Adjust Cart Item Quantity
from django.shortcuts import render, redirect, get_object_or_404
from .models import CartItem
from django.contrib import messages

def adjust_cart_item(request, cart_item_id):
    # Get the cart item by ID
    cart_item = get_object_or_404(CartItem, id=cart_item_id)

    if request.method == "POST":
        # Get quantity from POST data
        try:
            quantity = int(request.POST.get("quantity"))

            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, f"Updated {cart_item.product.name} quantity to {quantity}.")
            else:
                cart_item.delete()  # Remove item if quantity is 0
                messages.warning(request, f"Removed {cart_item.product.name} from cart.")
        except ValueError:
            messages.error(request, "Invalid quantity input.")

    return redirect("view_cart")

# Place Order (after checking cart)
from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, Order, CartItem
from django.contrib import messages
from django.utils.timezone import now
@login_required

def place_order(request):
    cart = get_object_or_404(Cart, user=request.user)

    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address')

        if not shipping_address:
            messages.error(request, "Shipping address is required.")
            return redirect('view_cart')  # If no shipping address provided

        # Create a list to store order details
        order_items = []
        total_price = 0

        for item in cart.items.all():
            order = Order.objects.create(
                product=item.product,
                quantity=item.quantity,
                total_price=item.total_price(),
                shipping_address=shipping_address,
                ordered_by_username=request.user.username,
                ordered_at=now()
            )
            order_items.append(order)
            total_price += order.total_price

            # Update product quantity in stock
            item.product.quantity -= item.quantity
            item.product.save()

        # Clear cart after placing order
        cart.items.all().delete()

        # Redirect to the receipt page with order details
        return render(request, 'receipt.html', {
            'order_items': order_items,
            'total_price': total_price,
            'shipping_address': shipping_address,
            'order_date': now()
        })

    return render(request, 'place_order.html', {'cart': cart})



# Logout View
def logout_view(request):
    logout(request)
    return redirect('login')
# In views.py
from django.shortcuts import render
from .models import Product
from .forms import ProductForm

def crud_view(request):
    products = Product.objects.all()
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('crud')  # Redirect to CRUD page after successful update
    else:
        form = ProductForm()
    return render(request, 'crud.html', {'form': form, 'products': products})
