from django.urls import path
from medicines import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='About'),
    path('contact/', views.contact, name='Contact'),
    path("search/", views.search, name="Search"),
    path('tracker/', views.tracker, name='Tracker'),
    path('services/', views.services, name='Services'),
    path('store/', views.store, name='Store'),
    path('checkout/', views.checkout, name='Checkout'),
    path('cartitems/', views.cartitems, name='cartitems'),
    path('product/<int:myid>', views.prodView, name='ProductView'),
    path("login/", views.handleLogin, name="HandleLogin"),
    path("logout/", views.handleLogout, name="HandleLogout"),
    path('register/', views.register, name='Register'),
    path("handlerequest/", views.handlerequest, name="HandleRequest"),

]
