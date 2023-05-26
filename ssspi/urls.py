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
    path('results/', results, name='results'),
    path('simulacion/<int:id>/', simulacion_detail, name='simulacion_detail'),
    path('simulacion/<int:id>/delete/', simulacion_delete, name='simulacion_delete'),
    path('simulacion/<int:id>/edit/', simulacion_update, name='simulacion_update'),
    path('simulacion/<int:simulacion_id>/descargar/', descargar_archivo, name='descargar_archivo')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)