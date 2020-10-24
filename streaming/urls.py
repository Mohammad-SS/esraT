from django.contrib import admin
from django.urls import path, include
from streaming import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  # Archive Urls :
                  path('archive/showAll/', views.showArchive),
                  path('archive/showNewArchive/', views.showNewArchive),
                  path('archive/searchArchive/', views.searchInArchive),
                  path("archive/video/<int:id>", views.downloadItemById),

                  # Users Urls :
                  path('user/register/', views.registerNewUser),
                  path('user/login/', views.loginUsers),
                  path('user/logout/', views.logOut),
                  path('user/forgetPassword/', views.forgetPassword),
                  path('user/changePassword/', views.changePassword),
                  path('user/editData/', views.changeUserDataByUser),
                  path('user/deleteAccount/', views.deleteAccountByUser),
                  path('user/getUserData/', views.getUserData),

                  # Conductor Urls :
                  path('conductor/showAll/', views.showConductor),
                  # Live Urls :
                  path('live/', views.showLive),

                  # Only Mobile App :
                  path('homepage/', views.getHomePage),

                  path('checkConnection', views.checkConnection)
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
