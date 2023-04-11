from rest_framework import serializers
from .models import Sector, Aplicacion, Proceso


class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = '__all__'


class AplicacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aplicacion
        fields = '__all__'


class ProcesoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proceso
        fields = '__all__'