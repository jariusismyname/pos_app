from django.urls import path
from . import views

urlpatterns = [
    path('admin-login/', views.custom_admin_login, name='admin-login'),  # Custom admin login page
    path('login/', views.login_view, name='login'),  # Regular login page for customers
    path('signup/', views.signup_view, name='signup'),  # Signup page
    path('products/', views.products_view, name='products'),  # Products page
    path('crud/', views.crud_view, name='crud'),  # CRUD page (admin only)
    path('place_order/<int:product_id>/', views.place_order, name='place_order'),  # Order page
    path('logout/', views.logout_view, name='logout'),  # Logout view
]
