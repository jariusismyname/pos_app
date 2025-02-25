from django.urls import path
from . import views
from django.urls import path, include
from django.shortcuts import redirect

def redirect_to_login(request):
    return redirect('/login/')  # Redirect root URL to /login/

urlpatterns = [
        path('', redirect_to_login),  # 👈 Redirect root URL `/` to `/login/`

    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('adjust-cart-item/<int:cart_item_id>/', views.adjust_cart_item, name='adjust_cart_item'),
    path('place-order/', views.place_order, name='place_order'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete-product'),  # Delete product action
    path('edit-product/<int:product_id>/', views.edit_product, name='edit-product'),  # Edit product page
    path('admin-login/', views.custom_admin_login, name='admin-login'),  # Custom admin login page
    path('login/', views.login_view, name='login'),  # Regular login page for customers
    path('signup/', views.signup_view, name='signup'),  # Signup page
    path('products/', views.products_view, name='products'),  # Products page
    path('crud/', views.crud_view, name='crud'),  # CRUD page (admin only)
    path('logout/', views.logout_view, name='logout'),  # Logout view
]
