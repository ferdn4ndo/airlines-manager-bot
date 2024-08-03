from django.urls import path

from api.views import LineViewSet

from .route_names import RouteNames

urlpatterns = [
    path('', LineViewSet.as_view({'get': 'list'}), name=RouteNames.ROUTE_LINES),
    path('<slug:slug>', LineViewSet.as_view({'get': 'read'}), name=RouteNames.ROUTE_LINE),
]
