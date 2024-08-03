from django.urls import path

from api.views import CronJobView

urlpatterns = [
    path('run', CronJobView.as_view()),
]
