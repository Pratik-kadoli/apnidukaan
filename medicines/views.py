from django.shortcuts import render, redirect
from django.http import HttpResponse

from django.contrib import messages
from .models import Contact, Product, Orders, OrderUpdate
import json 
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from PayTm import Checksum


MERCHANT_KEY = '_UdKStzYXAvtmggq';

# Create your views here.

def index(request):
    return render(request, "index.html")



def store(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category = cat)
        allProds.append(prod)

    params = {'allProds' : allProds}
    return render(request,'store.html', params)

def searchMatch(query, item):
    '''return True only if query matches the item'''
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else: 
        return False

def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category = cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]
        if len(prod) != 0:
            allProds.append(prod)
        else:
            pass


    params = {'allProds' : allProds, 'msg' : ""}
    if len(allProds) == 0 or len(query) == 4:
        params = {'msg' : "Please make sure to enter relevant search query"}
    return render(request,'search.html', params)

def about(request):
    return render(request, "about.html")

def contact(request):   
    if request.method == "POST":
        name = request.POST.get('name','')
        email = request.POST.get('email','')
        phone = request.POST.get('phone','')
        desc = request.POST.get('desc','')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        send_mail(
            'Message from BigDukaan',
            desc,
            'from_shopizzy@gmail.com',
            [email],
            fail_silently=False,
        )
        thank = True
        return render(request,'contact.html', {'thank' : thank})
    return render(request,'contact.html')

def services(request):
    return render(request, "services.html")

def cartitems(request):
    if request.user.is_anonymous:
        params = {'msg' : "You need to Login First"}
        return render(request,'index.html', params)
    return render(request, "cartitems.html")

def tracker(request):
    if request.user.is_anonymous:
        params = {'msg' : "You need to Login First"}
        return render(request,'index.html', params)
    if request.method == "POST":
        OrderId = request.POST.get('OrderId','')
        email = request.POST.get('email','')
        try:
            order = Orders.objects.filter(order_id=OrderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=OrderId)
                updates = []
                for item in update:
                    updates.append({'text' : item.update_desc, 'time' : item.timestamp})
                    response = json.dumps({"status" : "success", "updates" : updates,"itemsJson" : order[0].items_json}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status" : "noitem"}')
        except Exception as e:
            return HttpResponse('{"status" : "error"}')
    return render(request,'tracker.html')


def prodView(request, myid):    
    # fetch the product using the id
    product = Product.objects.filter(id = myid)
    return render(request, "prodView.html", {'product' : product[0]})

def checkout(request):
    if request.user.is_anonymous:
        params = {'msg' : "You need to Login First"}
        return render(request,'index.html', params)
    if request.method == "POST":
        items_json = request.POST.get('itemsJson','')
        name = request.POST.get('name','')
        amount = request.POST.get('amount','')
        email = request.POST.get('email','')
        address = request.POST.get('address1','') + " " + request.POST.get('address2','')
        city = request.POST.get('city','')
        state = request.POST.get('state','')
        zip_code = request.POST.get('zip_code','')
        contact = request.POST.get('contact','')
        order = Orders(items_json=items_json, name=name, email=email, address=address, city=city, state=state, zip_code=zip_code, contact=contact, amount=amount)
        order.save()
        update = OrderUpdate(order_id=order.order_id, update_desc="The Order has been Placed")
        update.save()
        thank = True
        id = order.order_id
        # return render(request,'thankyou.html', {'thank' : thank, 'id' : id})
        # Request Paytm to transfer the amount to your account after payment by user
        param_dict = {
            
            'MID':'fezdCq12654386461620',
            'ORDER_ID': str(order.order_id),
            'TXN_AMOUNT': str(amount),
            'CUST_ID': email,
            'INDUSTRY_TYPE_ID':'Retail',
            'WEBSITE':'WEBSTAGING',
            'CHANNEL_ID':'WEB',
            'CALLBACK_URL':'http://127.0.0.1:8000/handlerequest/',
        
        }
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
        return render(request, 'paytm.html', {'param_dict' : param_dict})
    return render(request,'checkout.html')

@csrf_exempt
def handlerequest(request):
    # paytm will send you a post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]
    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('Order successfull')
        else:
            print('Order was not successfull because '+ response_dict['RESPMSG'])

    return render(request, 'paymentstatus.html', {'response' : response_dict})


def register(request):
    if request.method == "POST":
        # get the post parameters
        username = request.POST['username']
        email    = request.POST['signupemail']
        # contact    = request.POST['contact']
        pass1    = request.POST['pass1']
        pass2    = request.POST['pass2']

        # check for errorneous inputs
        if username == "" and email == "" and pass1 == "" and pass2 == "" :
            params = {'msg' : "You need to fill all the fields"}
            return render(request,'register.html', params)
        if len(username) > 10:
            params = {'msg' : "Username should be less than 10 Characters"}
            return render(request,'register.html', params)
        # if not username.isalnum():
        #     params = {'msg' : "Username should only contains letters and numbers"}
        #     return render(request,'register.html', params)

        if pass1 != pass2:
            params = {'msg' : "Password not Match"}
            return render(request,'register.html', params)

        newuser = User.objects.filter(username=username)
        if newuser:
            params = {'msg' : "This Username is Already been taken"}
            return render(request,'register.html', params)

        else:
            myuser = User.objects.create_user(username, email, pass1)
            # myuser = User.objects.create_user(username, pass1)
            myuser.save()
            params = {'successmsg' : "Account Created Successfully"}
            return render(request,'register.html', params)
    # else:
    #     login_params = True
    #     return render(request, 'index.html', {'login_params' : login_params})
    else:
        return render(request, 'register.html')

def handleLogin(request):
    if request.method == "POST":
        # get the post parameters
        loginusername = request.POST['loginusername']
        loginpassword = request.POST['loginpassword']
        user = authenticate(username=loginusername, password=loginpassword)

        if user is not None:
            login(request, user)
            params = {'successmsg' : "Login Successful"}
            return render(request,'login.html', params)
            # popupLogin = True
            # return render(request, 'index.html', {'popupLogin' : popupLogin})
        else:
            params = {'msg' : "username or password not correct"}
            return render(request,'login.html', params)
    else:
        return render(request, 'login.html')

def handleLogout(request):
    logout(request)
    params = {'logoutmsg' : "Logged Out Successful"}
    return render(request,'index.html', params)

