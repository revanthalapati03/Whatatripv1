from django.urls import path, include

from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    path('register/', views.register, name="register"),
    path('forgotpassword/', views.forgotpass, name="forgotpass"),
    path('profile/', views.profile, name="profile"),
    path('resetpass/', views.resetpass, name="resetpass"),
    path('about/', views.about, name="about"),
    path('contact/', views.contact, name="contact"),
    path('discover/',views.discover, name="discover"),
    path('package/<title>/',views.packagedesc, name="package"),

]

