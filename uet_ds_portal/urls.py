from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Custom Admin Site Header & Title
admin.site.site_header = "UET Data Science Department Portal"
admin.site.site_title = "UET DS Portal Admin"
admin.site.index_title = "Department Administration & Management"

handler404 = 'apps.papers.views.custom_404_view'
handler500 = 'apps.papers.views.custom_500_view'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('timetable/', include('apps.timetable.urls', namespace='timetable')),
    path('seniors/', include('apps.seniors.urls', namespace='seniors')),
    path('', include('apps.papers.urls', namespace='papers')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
