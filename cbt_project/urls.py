from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Include the 'accounts' app URLs under the /api/accounts/ path
    path('api/accounts/', include('accounts.urls')),
]
