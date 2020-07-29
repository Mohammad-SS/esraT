from django.contrib import admin
from django.urls import path, include
from adminpanel import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  # Archive Urls :
                  path('login', views.login , name="login"),
                  path('home', views.homePage , name="home"),
                  path('settings', views.settings , name="setting"),
                  path('conductor', views.conductor, name="conductor"),
                  path('postHandler', views.postHandler, name="postHandler"),
                    path("logout" , views.logOut , name='logout')
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
