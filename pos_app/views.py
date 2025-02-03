from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import LoginForm, SignUpForm, ProductForm
from .models import Product, CustomUser, Order
from django.shortcuts import render, redirect
from django.contrib import messages

def custom_admin_login(request):
    if request.method == 'POST':
        # Check if the password is correct
        password = request.POST.get('password')
        if password == "password":
            # Redirect to the crud page for admin
            return redirect('crud')  
        else:
            # Show an error message if password is incorrect
            messages.error(request, "Incorrect password!")
            return render(request, 'admin_login.html')  # Re-render the login page
    return render(request, 'admin_login.html')  # Show login page on GET request

def welcome(request):
    return render(request, 'welcome.html')
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            try:
                # Get the user based on username
                user = CustomUser.objects.get(username=form.cleaned_data['username'])
            except CustomUser.DoesNotExist:
                messages.error(request, "User does not exist")
                return render(request, 'login.html', {'form': form})

            # Check if password matches
            if user.check_password(form.cleaned_data['password']):
                login(request, user)

                # # If user is admin (staff), redirect to the CRUD page
                # if user.is_staff:
                #     return redirect('crud')
                
                # If user is a regular customer, redirect to the products page
                return redirect('products')
            else:
                messages.error(request, "Incorrect password")
                return render(request, 'login.html', {'form': form})

    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


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

def crud_view(request):
    
    products = Product.objects.all()
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('crud')
    else:
        form = ProductForm()
    return render(request, 'crud.html', {'form': form, 'products': products})

def products_view(request):
    products = Product.objects.filter(quantity__gt=0)
    return render(request, 'products.html', {'products': products})

def logout_view(request):
    logout(request)
    return redirect('login')
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Product, Order

@login_required
def place_order(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return redirect('products')  # Handle the case where the product does not exist

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity'))
        shipping_address = request.POST.get('shipping_address')

        if quantity > product.quantity:
            return render(request, 'place_order.html', {
                'product': product,
                'error': 'Not enough stock available'
            })

        # If the user is authenticated, use their username; otherwise, set as "guest"
        if request.user.is_authenticated:
            ordered_by = request.user.username
        else:
            ordered_by = "guest"  # Set a default for guests

        # Update product quantity
        product.quantity -= quantity
        product.save()

        # Create the order
        Order.objects.create(
            product=product,
            quantity=quantity,
            total_price=quantity * product.price,
            shipping_address=shipping_address,
            ordered_by_username=ordered_by,  # Ensure you're using this field correctly
        )

        # Redirect to the products page after the order is placed
        return redirect('products')

    return render(request, 'place_order.html', {'product': product})
