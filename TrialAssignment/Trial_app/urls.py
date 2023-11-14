from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
urlpatterns = [
    path('api/v1/login/', views.UserLoginView.as_view()),
    path('api/v1/logout/', views.UserLogoutView.as_view()),
    path('api/v1/users/<int:id>/', views.UserDetailView.as_view()),
    path('api/v1/countries/', views.CountryDetailView.as_view()),
    path('api/v1/sales/', views.FileUploadView.as_view()),
    path('api/v1/uploadfile/', views.UploadFileDetail.as_view()),
    path('api/v1/sales_data/', views.SalesDataDetail.as_view()),
    path('api/v1/sale_statistics/', views.SalesStatisticsView.as_view()),
    path('api/v1/sales_data/<int:id>/', views.SalesDataUpdateDelete.as_view())
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)