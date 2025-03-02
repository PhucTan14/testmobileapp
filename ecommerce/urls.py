
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler404, handler500

urlpatterns = [
    # thêm đường dẫn đến app accounts
   
	path('admin/', admin.site.urls),
    path('', include('allauth.urls')),
	path('', include('store.urls')),    
	path('cart/', include('cart.urls')),
]

if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'store.views.error_404'
handler500 = 'store.views.error_500'

# python manage.py migrate
# python manage.py loaddata data.json
# python manage.py runserver