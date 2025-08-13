from django.urls import path
from . import views  # Ensure this import works correctly

from django.urls import path
from . import views

urlpatterns = [
    # Regular page views
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('booking/', views.booking, name='booking'),
    path('services/', views.services, name='services'),
    path('media/', views.media, name='media'),
    path('contact/', views.contact, name='contact'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    
    # API endpoints
    path('api/test/', views.test_api, name='test_api'),
    path('api/bookings/', views.create_booking, name='create_booking'),
    path('api/dashboard/', views.list_bookings, name='list_bookings'),
    path('export-contacts/', views.export_contacts, name='export_contacts'),
    path('contact/', views.contact_view, name='contact'),
]