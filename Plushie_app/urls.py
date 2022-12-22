from django.urls import path
from . import views

urlpatterns = [
    path('',views.home, name='home'),
    path('collections',views.collections,name="collections"),
    path('collections/<str:slug>', views.collectionsview, name="collectionsview"),
    path('collections/<str:cate_slug>/<str:prod_slug>',views.productview,name="productview"),
    path('register/',views.register, name="register"),
    path('login/',views.loginpage, name='loginpage'),
    path('logout/',views.logoutpage, name="logout"),
    path('add-to-cart',views.addtocart, name="addtocart"),
    path('cart',views.viewcart,name="cart"),
    path('update-cart',views.updatecart, name="updatecart"),
    path('delete-cart-item',views.deletecartitem, name="deletecartitem"),
    path('wishlist',views.wishlist,name="wishlist"),
    path('add-to-wishlist',views.addtowishlist, name="addtowishlist"),
    path('delete-wishlist-item', views.deletewishlist, name="deletewishlist"),
    path('checkout', views.checkout, name="checkout"),
    path('place-order',views.placeorder,name="placeorder"),
    path('my-orders', views.orders, name="myorders"),
    path('view-order/<str:t_no>',views.orderview,name="orderview")
]