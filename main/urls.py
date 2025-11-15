from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('courses/', views.courses_list, name='courses_list'),
    path('course/<slug:slug>/', views.course_detail, name='course_detail'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('checkout/<slug:slug>/', views.create_checkout, name='create_checkout'),
    path('payment/verify/', views.verify_payment, name='verify_payment'),
    path("contact/", views.contact, name="contact"),
    path("payment/success/", views.payment_success, name="payment_success"),
    path("payment/failed/", views.payment_failed, name="payment_failed"),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('contact/', views.contact, name='contact'),



]


