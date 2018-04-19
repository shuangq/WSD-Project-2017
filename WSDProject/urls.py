from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # admin pages
    path('admin/', admin.site.urls),
    # shop urls
    path('', include('shop.urls')),
    # authentication urls
    path('accounts/', include('authentication.urls')),

]
