from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework import generics
from .models import Sector, Aplicacion, Proceso
from .serializers import SectorSerializer, AplicacionSerializer, ProcesoSerializer

class SectorAPIView(generics.ListAPIView):
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer


class AplicacionAPIView(generics.ListAPIView):
    serializer_class = AplicacionSerializer

    def get_queryset(self):
        sector_id = self.kwargs['sector_id']
        return Aplicacion.objects.filter(sector_id=sector_id)


class ProcesoAPIView(generics.ListAPIView):
    serializer_class = ProcesoSerializer

    def get_queryset(self):
        aplicacion_id = self.kwargs['aplicacion_id']
        return Proceso.objects.filter(aplicacion_id=aplicacion_id)

# class FormSim(TemplateView):
#     template_name = 'formsim.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['sectores'] = SectorSerializer(Sector.objects.all(), many=True).data
#         context['aplicaciones'] = {}
#         context['procesos'] = {}
#         return context


