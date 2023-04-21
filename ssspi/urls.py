from django.urls import path, include
from ssspi.views import *
from django.contrib.auth import views as auth_views
#from django.contrib.auth.views import logout_then_login
from django.conf import settings
from django.conf.urls.static import static
from .views import CustomLogoutView


urlpatterns = [
    path('',index,name='index'),
    path('simulacion/',simulacion,name='simulacion'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', register, name='registro'),
    path('acerca/', acerca, name='acerca'),
    path('contacto/',contacto, name='contacto'),
    path('dashboard/',dashboardView, name='dashboard'),
    path('update_profile/', update_profile, name='update_profile'),
    path('update_aplicacion/', update_aplicacion, name='update_aplicacion'),
    path('update_profile/', update_profile, name='update_profile'),
    path('resultados/', resultados, name='resultados'),
    #path('pdf/',views.html_to_pdf, name='pdf_view'),
    #path('apiern/', views.apiern, name='apiern'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)