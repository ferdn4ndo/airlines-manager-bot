from django.urls import path

from api.views import AirportViewSet

from .route_names import RouteNames

urlpatterns = [
    path('', AirportViewSet.as_view({'get': 'list'}), name=RouteNames.ROUTE_AIRPORTS),
    path('<slug:slug>', AirportViewSet.as_view({'get': 'read'}), name=RouteNames.ROUTE_AIRPORT),
]
