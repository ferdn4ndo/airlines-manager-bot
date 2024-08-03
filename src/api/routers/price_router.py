from django.urls import path

from api.views import PriceViewSet

from .route_names import RouteNames

urlpatterns = [
    path('', PriceViewSet.as_view({'get': 'list'}), name=RouteNames.ROUTE_PRICES),
    path('<slug:slug>', PriceViewSet.as_view({'get': 'read'}), name=RouteNames.ROUTE_PRICE),
]
