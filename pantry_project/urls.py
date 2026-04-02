from django.contrib import admin
from django.urls import path
from pantry.views import item_list   # <-- direct import

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', item_list),  # <-- DIRECT mapping
]