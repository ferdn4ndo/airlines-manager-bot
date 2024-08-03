from django.urls import include, path
from django.contrib import admin

from api.forms.user_forms import CustomUserAdmin
from api.models.user_model import CustomUser
from api.routers import doc_router, airport_router, cronjob_router, health_router, demand_router, price_router, \
    line_router

admin.site.register(CustomUser, CustomUserAdmin)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('cronjob/', include(cronjob_router.urlpatterns)),
    path('airports/', include(airport_router.urlpatterns)),
    path('demands/', include(demand_router.urlpatterns)),
    path('prices/', include(price_router.urlpatterns)),
    path('lines/', include(line_router.urlpatterns)),
    path('health/', include(health_router.urlpatterns)),
    path('docs/', include(doc_router.urlpatterns)),
]
