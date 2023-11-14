from rest_framework import serializers
from .models import *


class UserLoginSerializer( serializers.ModelSerializer):
     class Meta:
            model = CustomUser
            fields = ['id', 'username', 'first_name', 'last_name', 'email', 'gender', 'age', 'country', 'city']

class CountrySerializer(serializers.ModelSerializer):
       cities = serializers.SerializerMethodField()
       class Meta:
              model = Country
              fields = ["id", "name", "cities"]

       def get_cities(self, obj):
              data = []
              for city in obj.city_set.all():
                     aa = {
                            "id":city.id,
                            "name":city.name
                            }
                     data.append(aa)

              return data
       
class FileUploadSerializer(serializers.ModelSerializer):

       class Meta:
              model = UploadedFile
              fields = "__all__"
       
class SalesDataSerializer(serializers.ModelSerializer):

       class Meta:
              model = SalesData
              fields = ['date', 'product', 'sales_number', 'revenue']