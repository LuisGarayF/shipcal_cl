from django.urls import path
from . import views

app_name = 'sims'

urlpatterns = [
    path('api/sectores/', views.SectorListAPIView.as_view(), name='sectores'),
    path('api/aplicaciones/<int:sector_id>/', views.AplicacionListAPIView.as_view(), name='aplicaciones'),
    path('api/procesos/<int:aplicacion_id>/', views.ProcesosListAPIView.as_view(), name='procesosos'),
    path('formsim/', views.FormSim.as_view(), name='formsim'),
]
