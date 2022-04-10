from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import auth as authe
import pyrebase
from .models import *
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.staticfiles.storage import staticfiles_storage
from django.templatetags.static import static
from .models import *
from django.core.files.storage import FileSystemStorage
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


data = os.path.abspath(os.path.dirname(__file__)) + "/serviceAccountKey.json"
cred = credentials.Certificate(data)
firebase_admin.initialize_app(cred)


# doc_ref = db.collection(u'BANNERS').document(u'BANNER_1')

# doc = doc_ref.get()
# if doc.exists:
#     print(f'Document data: {doc.to_dict()}')
# else:
#     print(u'No such document!')


config = {
    'apiKey': "AIzaSyBmmJ95nUnYed0S8NZm4bEVwJ1ij65m8Zk",
    'authDomain': "testtrip1.firebaseapp.com",
    'projectId': "testtrip1",
    'storageBucket': "testtrip1.appspot.com",
    'messagingSenderId': "228068790363",
    'appId': "1:228068790363:web:552209a4d0d5b0bce8ef7e",
    'measurementId': "G-5Y4G78DT28",
    'databaseURL': "https://testtrip1-default-rtdb.firebaseio.com"
}

firebase = pyrebase.initialize_app(config)

firedb = firestore.client()
auth = firebase.auth()
database = firebase.database()
storage = firebase.storage()


def home(request):
    try:
        idtoken = request.session['uid']
        user = auth.get_account_info(idtoken)
        user = user['users'][0]['localId']
        email = database.child("users").child(user).child('email').get().val()
        fullname = database.child('users').child(user).child('full_name').get().val()
        profileurl=storage.child("images/profile/"+user).get_url(None)
        if profileurl==None:
            profileurl="https://github.com/danishlaeeq/Facebook-Style-Profile-Dropdown-Menu/blob/main/assets/img/user2.jpg?raw=true"
        
        if email!= None:
            return render(request, 'accounts/index.html',{'email':email, 'fullname':fullname,'profileurl':profileurl})
        
        return render(request, 'accounts/index.html',{'email':email, 'fullname':fullname,'profileurl':profileurl})
    
    except:    
        return render(request, 'accounts/index.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = auth.sign_in_with_email_and_password(email,password)
            session_id=user['idToken']
            request.session['uid']=str(session_id)
            user = auth.get_account_info(str(session_id))
            user = user['users'][0]['localId']
            fullname = database.child('users').child(user).child('full_name').get().val()
            profileurl=storage.child("images/profile/"+user).get_url(None)
            
            return render(request, 'accounts/index.html',{'email':email, 'fullname':fullname,'profileurl':profileurl})
        except:
            message = "invalid Credentials"
            return render(request, 'accounts/login.html',{'messg':message})

    context = {}
    return render(request, 'accounts/login.html', context)

def logout(request):
    try:
        del request.session['uid']
    except KeyError:
        pass
    return render(request, 'accounts/index.html')

def register(request):
    if request.method == 'POST':
        fullname=request.POST.get('fullname')
        phone =  request.POST.get('phone')
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = auth.create_user_with_email_and_password(email,password)
            auth.send_email_verification(user['idToken'])
            session_id=user['idToken']
            request.session['uid']=str(session_id)
            user = auth.get_account_info(str(session_id))
            user = user['users'][0]['localId']

            data = {"email":email, "full_name":fullname, "phone":phone}
            database.child("users").child(user).set(data)
            profileimage="static//images/whatatriplogo1.png"
            storage.child("images/profile/"+user).put(profileimage)
            profileurl=storage.child("images/profile/"+user).get_url(None)
            message="Account created succesfully please verify in Mail"
            return render(request, 'accounts/index.html',{'email':email, 'fullname':fullname,'profileurl':profileurl, 'messg':message})
        except:
            message="email already exists"
            return render(request, 'accounts/register.html',{'messg':message})
    
    context = {}
    return render(request, 'accounts/register.html', context)
   
def forgotpass(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            auth.send_password_reset_email(email)
            message="Password reset mail sent succesfully"
            return render(request, 'accounts/index.html',{'messg':message})
        except:
            message="incorrect mail ID"
            return render(request, 'accounts/forgotpass.html',{'messg':message})
    context = {}
    return render(request, 'accounts/forgotpass.html', context)

def resetpass(request):
    idtoken = request.session['uid']
    user = auth.get_account_info(idtoken)
    user = user['users'][0]['localId']
        
    email = database.child("users").child(user).child('email').get().val()
    fullname = database.child('users').child(user).child('full_name').get().val()
    profileurl=storage.child("images/profile/"+user).get_url(None)
    if profileurl==None:
        profileurl="https://github.com/danishlaeeq/Facebook-Style-Profile-Dropdown-Menu/blob/main/assets/img/user2.jpg?raw=true"
    
    if email!= None:
        auth.send_password_reset_email(email)
        message="Password reset mail sent succesfully"
        return render(request, 'accounts/index.html',{'email':email, 'fullname':fullname,'profileurl':profileurl,'messg':message})
   
    return render(request, 'accounts/index.html')


def profile(request):
    idtoken = request.session['uid']
    user = auth.get_account_info(idtoken)
    user = user['users'][0]['localId']
        
    email = database.child("users").child(user).child('email').get().val()
    fullname = database.child('users').child(user).child('full_name').get().val()
    firstname=list(map(str, fullname.split(' ')))[0]
    if len(list(map(str, fullname.split(' '))))>1:
        lastname=list(map(str, fullname.split(' ')))[1]
    else:
        lastname=' '
    phone = database.child("users").child(user).child('phone').get().val()
    profileurl=storage.child("images/profile/"+user).get_url(None)

    if request.method == 'POST':
        firstname=request.POST.get('firstname')
        lastname=request.POST.get('lastname')
        if lastname!=None:
            fullname=' '.join([firstname,lastname])
        else:
            fullname=firstname
        phone =  request.POST.get('phone')
        email = request.POST.get('email')
        profilepic = request.FILES['profilepic']
        fss = FileSystemStorage()
        file = fss.save(profilepic.name, profilepic)
        profileimage = fss.url(file)
        profileimage = "static/"+ profileimage
        context={'full_name':fullname, 'email':email,'phone':phone}
        database.child("users").child(user).update(context)
        storage.child("images/profile/"+user).put(profileimage)
        profileurl=storage.child("images/profile/"+user).get_url(None)

        
    context={'email':email, 'fullname':fullname,'firstname':firstname,'lastname':lastname, 'phone':phone,'profileurl':profileurl}
    return render(request, 'accounts/profilepage.html',context)

def about(request):
    try:
        idtoken = request.session['uid']
        user = auth.get_account_info(idtoken)
        user = user['users'][0]['localId']
        email = database.child("users").child(user).child('email').get().val()
        fullname = database.child('users').child(user).child('full_name').get().val()
        profileurl=storage.child("images/profile/"+user).get_url(None)
        if profileurl==None:
            profileurl="https://github.com/danishlaeeq/Facebook-Style-Profile-Dropdown-Menu/blob/main/assets/img/user2.jpg?raw=true"
        
        if email!= None:
            return render(request, 'accounts/about.html',{'email':email, 'fullname':fullname,'profileurl':profileurl})
        
        return render(request, 'accounts/about.html',{'email':email, 'fullname':fullname,'profileurl':profileurl})
    
    except:    
        return render(request, 'accounts/about.html')

def contact(request):
    if request.method == 'POST':
        context={}
        email = request.POST.get('email')
        name = request.POST.get('name')
        message=request.POST.get('message')
        message=' // '.join([email,name,message])
        send_mail("Contact Form",message,settings.EMAIL_HOST_USER,['whatatrip.ah@gmail.com'],fail_silently=False)

    try:
        context={}
        idtoken = request.session['uid']
        user = auth.get_account_info(idtoken)
        user = user['users'][0]['localId']
        email = database.child("users").child(user).child('email').get().val()
        fullname = database.child('users').child(user).child('full_name').get().val()
        profileurl=storage.child("images/profile/"+user).get_url(None)
        if profileurl==None:
            profileurl="https://github.com/danishlaeeq/Facebook-Style-Profile-Dropdown-Menu/blob/main/assets/img/user2.jpg?raw=true"
        if email!= None:
            context={'email':email, 'fullname':fullname,'profileurl':profileurl}
        return render(request, 'accounts/contact.html',context)   
    except:    
        return render(request, 'accounts/contact.html')

def discover(request):
    bannerss = firedb.collection(u'BANNERS').stream()
    top_tours = firedb.collection(u'TOP_TOURS').stream()
    latest_tours = firedb.collection(u'TOP_TOURS').stream()
    banners = []
    count =0
    for doc in bannerss:
        banner ={}
        banner['img'] = doc.to_dict()['icon']
        banner['place'] = doc.to_dict()['place']
        banner['desc'] = doc.to_dict()['desc']
        banners.append(banner)
        count = count+1
        # print(f'{doc.id} => {doc.to_dict()}')
    
    toptours=[]
    for doc in top_tours:
        toptour = {}
        toptour['img'] = doc.to_dict()['icon']
        toptour['price']=doc.to_dict()['price']
        toptour['title']=doc.to_dict()['title']
        toptours.append(toptour)

    latesttours=[]
    for doc in latest_tours:
        latesttour = {}
        latesttour['img'] = doc.to_dict()['icon']
        latesttour['price']=doc.to_dict()['price']
        latesttour['title']=doc.to_dict()['title']
        latesttours.append(latesttour)
    print(latesttours)
    context={
            "firstbanner":banners[0],
            "banners":banners[1::],
            "banlen" : list(i for i in range(count-1)),
            "toptours":toptours,
            "latesttours":latesttours,
            }
    try:
        idtoken = request.session['uid']
        user = auth.get_account_info(idtoken)
        user = user['users'][0]['localId']
        email = database.child("users").child(user).child('email').get().val()
        fullname = database.child('users').child(user).child('full_name').get().val()
        profileurl=storage.child("images/profile/"+user).get_url(None)
        if profileurl==None:
            profileurl="https://github.com/danishlaeeq/Facebook-Style-Profile-Dropdown-Menu/blob/main/assets/img/user2.jpg?raw=true"
        if email!= None:
            context['email']=email
            context['fullname']=fullname
            context['profileurl']=profileurl
        return render(request, 'accounts/discover.html',context )    
    except:    
        return render(request, 'accounts/discover.html',context )

def packagedesc(request, title='Maldives'):
    Tours = firedb.collection(u'TOURS').stream()
    latest_tours = firedb.collection(u'TOP_TOURS').stream()
    tour={}
    latesttours=[]
    for doc in latest_tours:
        latesttour = {}
        latesttour['img'] = doc.to_dict()['icon']
        latesttour['price']=doc.to_dict()['price']
        latesttour['title']=doc.to_dict()['title']
        latesttours.append(latesttour)
    for doc in Tours:
        if doc.to_dict()['product_title']==title:
            tour['title']=title
            tour['imagecount']=doc.to_dict()['no_of_product_images']
            tour['price']=doc.to_dict()['price']
            tour['desc']=doc.to_dict()['product_description']
            tourimages=[]
            for i in range(1,int(tour['imagecount'])+1):
                name='product_image_'+ str(i)
                img = doc.to_dict()[name]
                tourimages.append(img)
            tour['tourimages']=tourimages
            tour['latesttours']=latesttours
    try:
        idtoken = request.session['uid']
        user = auth.get_account_info(idtoken)
        user = user['users'][0]['localId']
        email = database.child("users").child(user).child('email').get().val()
        fullname = database.child('users').child(user).child('full_name').get().val()
        profileurl=storage.child("images/profile/"+user).get_url(None)
        if profileurl==None:
            profileurl="https://github.com/danishlaeeq/Facebook-Style-Profile-Dropdown-Menu/blob/main/assets/img/user2.jpg?raw=true"
        if email!= None:
            tour['email']=email
            tour['fullname']=fullname
            tour['profileurl']=profileurl
        return render(request, 'accounts/package.html',tour)    
    except:
        return render(request, 'accounts/package.html',tour)
     
    
    
    
    

    
        