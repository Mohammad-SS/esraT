from django.contrib import admin
from django.urls import path, include
from adminpanel import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  # Main Urls :
                  path('', views.login, name="login"),
                  path('home', views.homePage, name="home"),
                  path('settings', views.settings, name="setting"),
                  path('postHandler', views.postHandler, name="postHandler"),
                  path("logout", views.logOut, name='logout') ,

                  # Conductor Urls :
                  path('conductor', views.conductor, name="conductor"),
                  path('conductor/addNew', views.addNewConductorItem, name="newCondocturItem"),
                  path('conductor/editItem', views.editConductorItem, name="conductorEditor"),

                  # Archive Urls :
                  path('archive', views.archive, name="archive"),
                  path('archive/addNew', views.addNewArchiveItem, name="newArchiveItem"),
                  path('archive/editItem', views.editArchiveItem, name="archiveEditor"),

                  # User Managements Urls :
                  path('users', views.users, name="users"),
                  path('users/editItem', views.editUser, name="userEditor"),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
