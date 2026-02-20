from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from users.views import home

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', home, name='home'),
    path('admin/', include('custom_admin.urls')),
    path('users/', include('users.urls')),
    path('professionals/', include('professionals.urls')),
    path('products/', include('products.urls')),
    path('quotations/', include('quotations.urls')),
    path('bookings/', include('bookings.urls')),
    path('delivery/', include('delivery.urls')),
]

# Serve static and media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # No need to serve STATIC_URL manually in DEBUG mode; runserver does it automatically
    # and correctly finds both app-level (admin) and project-level static files.
else:
    # In production (DEBUG=False), you should really use a web server (Nginx/Apache) 
    # or ensure collectstatic is run and serve from STATIC_ROOT.
    # This is a fallback for local testing with DEBUG=False.
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    ]

handler404 = 'gciap.views.custom_404'

