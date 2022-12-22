from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.http.response import JsonResponse
from django.contrib.auth.decorators import login_required
import random

# Create your views here.
def home(request):
    trending_products=Product.objects.filter(trending=1)
    context={'trending_products':trending_products}
    return render(request,'index.html',context)

def collections(request):
    category=Category.objects.filter(status=0)
    context={'category':category}
    return render(request,'collections.html', context)    

def collectionsview(request,slug):
    if(Category.objects.filter(slug=slug,status=0)):
        products=Product.objects.filter(category_slug=slug)
        category=Category.objects.filter(slug=slug).first()
        context= {'products' : products, 'category': category}
        return render(request,'products.html', context)  
    else:
        messages.warning(request,"No Such Category Found") 
        return redirect('collections')   

def productview(request ,cate_slug,prod_slug):
    if (Category.objects.filter(slug=cate_slug,status=0)):
        if (Product.objects.filter(slug=prod_slug,status=0)):
            products=Product.objects.filter(slug=prod_slug,status=0).first
            context={'products':products}
        else:
            messages.warning(request,"No Such Product Found") 
            return redirect('collections') 
    else:
        messages.warning(request,"No Such Category Found") 
        return redirect('collections') 
    return render(request,"view.html",context)           

# login and user registration

def register(request):
    form=UserCreationForm()
    if request.method=='POST':
        form=UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Registered Successfully! Please Login to Continue")
            return redirect('/login')
    context={'form': form}
    return render(request,'register.html',context)

def loginpage(request):
    if request.user.is_authenticated:
        messages.warning(request,"You are already logged in!")
        return redirect('/')
    else:    
        if request.method=='POST':
            name=request.POST.get('username')
            pass_word=request.POST.get('password')
            user=authenticate(request, username=name, password=pass_word)

            if user is not None:
                login(request, user)
                messages.success(request,"Logged in Successfully!")
            else:
                messages.error(request,"Invalid Username or Password!")
                return redirect('/login')
    return render(request, 'login.html')  

def logoutpage(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request,"Logged out successfully!")
    return redirect('/')    

#add to cart

def addtocart(request):
    if request.method=='POST':
        if request.user.is_authenticated:
            prod_id=int(request.POST.get('product_id'))  
            product_check=Product.objects.get(id=prod_id)
            if(product_check):
                if(Cart.objects.filter(user=request.user.id,product_id=prod_id)):
                    return JsonResponse({'status':"Product already in cart"})
                else:
                    prod_qty=int(request.POST.get('product_qty'))

                    if product_check.quantity >= prod_qty:
                        Cart.objects.create(user=request.user,product_id=prod_id,product_qty=prod_qty)
                        return JsonResponse({'status':"Product added successfully"})
                    else:
                        return JsonResponse({'status':"Only"+str(product_check.quantity)+"quantity available"})    
            else:
                return JsonResponse({'status':"No such product found"})        
        else:
            return JsonResponse({'status:"Login to Continue'})  
    return redirect('/')             

@login_required(login_url='loginpage')
#cart view

def viewcart(request):
    cart=Cart.objects.filter(user=request.user)  
    context={'cart':cart}
    return render(request,'cart.html',context) 

def updatecart(request):
        if request.method=='POST':
            prod_id=int(request.POSt.get('product_id'))
            if(Cart.objects.filter(user=request.user,product_id=prod_id)):
                prod_qty=int(request.POST.get('product_qty'))
                cart=Cart.objects.get(product_id=prod_id, user=request.user)
                cart.product_qty=prod_qty
                cart.save()
                return JsonResponse({'status':"Updated Successfully!"})
            return redirect('/')  

def deletecartitem(request):
    if request.method=='POST':
        prod_id=int(request.POST.get('product_id'))
        if (Cart.objects.filter(user=request.user,product_id=prod_id)):
            cartitem=Cart.objects.get(product_id=prod_id,user=request.user)
            cartitem.delete()
        return JsonResponse({'status':"Deleted Successfully"})
    return redirect('/')                
                   
# wishlist

@login_required(login_url='loginpage')
def wishlist(request):
    wishlist=wishlist.objects.filter(user=request.user)
    context={'wishlist':wishlist}
    return render(request,'wishlist.html',context)

def addtowishlist(request):
    if request.method=='POST':
        if request.user.is_authenticated:
            prod_id=int(request.POST.get('product_id'))
            product_check=Product.objects.get(id=prod_id)
            if(product_check):
                if (Wishlist.objects.filter(user=request.user,product_id=prod_id)):
                    return JsonResponse({'status':"Product already in wishlist"})
                else:
                    Wishlist.objects.create(user=request.user,product_id=prod_id) 
                    return JsonResponse({'status':"Product added to wishlist"})   
            else:
                return JsonResponse({'status':"No such product found"})
        else:
            return JsonResponse({'status':"Login to continue"})
    return redirect('/')   

def deletewishlist(request):
    if request.method=='POST':
        if request.user.is_authenticated:
            prod_id=int(request.POST.get('product_id'))
            if (Wishlist.objects.filter(user=request.user,product_id=prod_id)):
                wishlistitem=Wishlist.objects.get(product_id=prod_id)
                wishlistitem.delete()
                return JsonResponse({'status':"Product removed from wishlist"})
            else:
                Wishlist.objects.create(user=request.user,product_id=prod_id) 
                return JsonResponse({'status':"Product not found in wishlist"})
        else:
            return JsonResponse({'status':"Login to continue"})
    return redirect('/')    

#checkout

@login_required(login_url='loginpage')
def checkout(request):
    rawcart=Cart.objects.filter(user=request.user)
    for item in rawcart:
        if item.product_qty > item.product.quantity:
            Cart.objects.delete(id=item.id)
    cartitems=Cart.objects.filter(user=request.user)
    total_price=0
    for item in cartitems:
        total_price=total_price+ item.product.selling_price*item.product_qty      

    userprofile=Profile.objects.filter(user=request.user).first()

    context={'cartitems':cartitems, 'total_price':total_price, 'userprofile':userprofile}        
    return render(request,"checkout.html", context)  

@login_required(login_url='loginpage')
def placeorder(request): 
    if request.method=='POST':

        currentuser=User.objects.filter(id=request.user.id).first()

        if not currentuser.first_name:
            currentuser.first_name=request.POST.get('fname')
            currentuser.last_name=request.POST.get('lname')
            currentuser.save()

        if not Profile.objects.filter(user=request.user):
            userprofile=Profile()
            userprofile.user=request.user  
            userprofile.phone=request.POST.get('phone')
            userprofile.address=request.POST.get('address')
            userprofile.city=request.POST.get('city')
            userprofile.state=request.POST.get('state')
            userprofile.country=request.POST.get('country')
            userprofile.pincode=request.POST.get('pincode') 
            userprofile.save() 

        neworder=Order()
        neworder.user=request.user
        neworder.fname=request.POST.get('fname')
        neworder.lname=request.POST.get('lname')
        neworder.email=request.POST.get('email')
        neworder.phone=request.POST.get('phone')
        neworder.address=request.POST.get('address')
        neworder.city=request.POST.get('city')
        neworder.state=request.POST.get('state')
        neworder.country=request.POST.get('country')
        neworder.pincode=request.POST.get('pincode')
        neworder.payment_mode=request.POST.get('payment_mode')

        cart=Cart.objects.filter(user=request.user)
        cart_total_price=0
        for item in cart:
            cart_total_price=cart_total_price+item.product.selling_price*item.product_qty

        neworder.total_price=cart_total_price
        trackno='plushie'+str(random.randint(1111111,9999999))  
        while Order.objects.filter(tracking_no=trackno) is None:
            trackno='plushie'+str(random.randint(1111111,9999999))  

        neworder.tracking_no=trackno
        neworder.save()

        neworderitems=Cart.objects.filter(user=request.user)
        for item in neworderitems :
            OrderItem.objects.create(
                order=neworder,
                product=item.product,
                price=item.product.selling_price,
                quantity=item.product_qty,
            )   

            #Decrease the product quantity from available stock

            orderproduct=Product.objects.filter(id=item.product_id).first()
            orderproduct.quantity=orderproduct.quantity-item.product_qty
            orderproduct.save()

       #Clear user's cart
        Cart.objects.filter(user=request.user).delete()

        messages.success(request,"Your order has been placed successfully")

    return redirect('/')    

# order checkout

def orders(request):
    orders=Order.objects.filter(user=request.user)
    context={'orders':orders}
    return render(request,"orders.html",context)

def orderview(request,t_no):
    order=Order.objects.filter(tracking_no=t_no).filter(user=request.user).first()
    orderitems=OrderItem.objects.filter(order=order)
    context={'order':order, 'orderitems':orderitems} 
    return render(request,"orderview.html", context)   