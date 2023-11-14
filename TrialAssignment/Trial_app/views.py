from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from .models import *
from rest_framework.parsers import FormParser, MultiPartParser
import csv
from django.db.models import Q

# Create your views here.

class UserLoginView(APIView):
       def post(self, request, *args, **kwargs):
              email = request.data['email']
              password = request.data['password']
              user = authenticate(request, email=email, password=password)
              if user is not None:
                     token = Token.objects.get_or_create(user=user)
                     return Response({'response':{'token':token[0].key, 'user_id':token[0].user_id}})
              else:
                     return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
              
class UserLogoutView(APIView):
       def post(self, request):
              request.auth.delete()
              return Response(status=status.HTTP_200_OK)
      
class UserDetailView(APIView):

       permission_classes = [IsAuthenticated]

       def get(self, request, id):
              queryset = CustomUser.objects.filter(id=id)
              if queryset is not None:
                     serializer = UserLoginSerializer(queryset, many=True)
                     return Response(serializer.data)
              else:
                     return Response({'error': 'Invalid user_id'}, status=status.HTTP_401_UNAUTHORIZED)
              
       def patch(self, request, id):
           queryset =get_object_or_404(CustomUser, id = id)
           serializer = UserLoginSerializer(queryset, data=request.data, partial=True)
           if serializer.is_valid():
                  serializer.save()
                  return Response(status=status.HTTP_200_OK)
          
           return Response(serializer.errors) 

class CountryDetailView(APIView):
       permission_classes = [IsAuthenticated]

       def get(self, request, *args, **kwargs):
              queryset = Country.objects.all()
              country_list = list(queryset)
              serializer = CountrySerializer(country_list, many=True)

              return Response(serializer.data)


class UploadFileDetail(APIView):
       permission_classes = [IsAuthenticated]

       def post(self, request, format = 'csv'):
              file_data = request.FILES['file']
              decoded_file = file_data.read().decode('utf-8').splitlines()
              csv_reader = csv.reader(decoded_file)
              header = next(csv_reader)
              data_list = []
              for row in csv_reader:
                            data_dict = dict(zip(header, row))
                            data_list.append(data_dict)
              return Response(data_list)
       
class FileUploadView(APIView):
       parser_classes = (MultiPartParser, FormParser)
       serializer_class = FileUploadSerializer
       permission_classes = [IsAuthenticated]

       def post(self, request, format='csv'):
              # import pdb;pdb.set_trace()
              data = request.data.copy()
              file_data = request.FILES['file']
              decoded_file = file_data.read().decode('utf-8').splitlines()
              csv_reader = csv.reader(decoded_file)
              data['uploaded_by'] = request.user.id
              serializer = self.serializer_class(data=data)
              if serializer.is_valid():
                            serializer.save()
                            header = next(csv_reader)
                            data_list = []
                            for row in csv_reader:
                                   data_dict = dict(zip(header, row))
                                   data_dict['created_by'] = request.user
                                   data_dict['file_name'] = serializer.instance
                                   data_list.append(data_dict)
                                   SalesData.objects.create(**data_dict)
                            return Response(serializer.data)
              else:
                     return Response(serializer.errors)


           
class SalesDataDetail(APIView):

       permission_classes = [IsAuthenticated]

       def get(self, request):
              sale_data = SalesData.objects.filter(created_by=request.user)
              serializer = SalesDataSerializer(sale_data, many=True)
              return Response(serializer.data)
       

class SalesDataUpdateDelete(APIView):

       permission_classes = [IsAuthenticated]

       def patch(self, request, id):
              queryset =get_object_or_404(SalesData, id = id)
              serializer = SalesDataSerializer(queryset, data=request.data, partial=True)
              if serializer.is_valid():
                     serializer.save()
                     return Response(status=status.HTTP_200_OK)
              
              return Response(serializer.errors) 
       
       def delete(self,request, id):
              instance = get_object_or_404(SalesData, id=id)
              instance.delete()
              return Response(status=status.HTTP_204_NO_CONTENT)

class SalesStatisticsView(APIView):

       permission_classes = [IsAuthenticated]

       def get(self, request ):
              sale_data = SalesData.objects.all()
              current_sales_data = sale_data.filter(created_by=request.user)
              curent_sales_number =  current_sales_data.values_list('sales_number', flat=True)
              curent_total_sales_number =  sum(map(float, curent_sales_number))
              current_revenue = current_sales_data.values_list('revenue', flat=True)
              current_total_revenue = sum(map(float, current_revenue))
              average_sales_for_current_user = current_total_revenue/curent_total_sales_number
              all_user_revenue =  sale_data.values_list('revenue', flat=True)
              all_user_sales_number = sale_data.values_list('sales_number', flat=True)
              all_user_total_revenue = sum(map(float, all_user_revenue))
              all_user_sales_number = sum(map(float, all_user_sales_number))
              average_sale_all_user = all_user_total_revenue/all_user_sales_number
              result_dict = {}
              data_dict = {}
              for item in current_sales_data:
                     product = item.product
                     revenue = item.revenue
                     sales_number = item.sales_number
                     if product in result_dict:
                            result_dict[product].append(float(revenue))
                            data_dict[product].append(float(sales_number))

                     else:
                            result_dict[product] = [float(revenue)]
                            data_dict[product] = [float(sales_number)]

              product_highest_revenue = {key:max(values) for key, values in result_dict.items() }
              product_highest_sales_number = {key:max(values) for key, values in data_dict.items() }
              max_revenue = max(product_highest_revenue.items(), key=lambda x: x[1])
              max_sales = max(product_highest_sales_number.items(), key=lambda x: x[1])

              product_highest_revenue_for_current_user = {"product_name":max_revenue[0],"price":max_revenue[1]}
              product_highest_sales_number_for_current_user = {"product_name":max_sales[0],"price": max_sales[1]}
              aa = current_sales_data.filter(revenue = max_revenue[1]).last()
              if aa:
                     highest_revenue_sale_for_current_user = {
                            "sale_id":aa.id,
                            "revenue":aa.revenue
                     }
              else:
                     highest_revenue_sale_for_current_user = None
              final_dict = {
                     "average_sales_for_current_user":average_sales_for_current_user,
                     "average_sale_all_user":average_sale_all_user,
                     "highest_revenue_sale_for_current_user":highest_revenue_sale_for_current_user,
                     "product_highest_revenue_for_current_user":product_highest_revenue_for_current_user,
                     "product_highest_sales_number_for_current_user":product_highest_sales_number_for_current_user
                      
                       }
             
              return Response(final_dict)
