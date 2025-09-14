# cattle_health_project/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # หน้า admin ของ Django
    path('admin/', admin.site.urls),

    # เชื่อมแอป cattle
    path('', include('cattle.urls')),
]
