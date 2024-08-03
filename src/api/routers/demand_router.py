from django.urls import path

from api.views import DemandViewSet

from .route_names import RouteNames

urlpatterns = [
    path('', DemandViewSet.as_view({'get': 'list'}), name=RouteNames.ROUTE_DEMANDS),
    path('<slug:slug>', DemandViewSet.as_view({'get': 'read'}), name=RouteNames.ROUTE_DEMAND),
]
