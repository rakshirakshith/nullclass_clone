from django.contrib import admin
from .models import Order, Payment, PurchasedCourse, Course, Lesson

admin.site.register(Order)
admin.site.register(Payment)
admin.site.register(PurchasedCourse)
admin.site.register(Course)
admin.site.register(Lesson)
