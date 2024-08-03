from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _

from .generic_audited_model import GenericAuditedModel


class Airport(GenericAuditedModel):

    am_id = models.IntegerField(null=True, verbose_name=_("The ID of the airport inside Airlines Manager"))
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("The airport name"))
    iata_code = models.CharField(max_length=3, null=True, blank=True, verbose_name=_("The airport IATA code"))
    city_name = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("The airport city name"))
    country_name = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("The airport country name"))
    country_flag_url = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("The airport country flag URL"))
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, verbose_name=_("The latitude of the airport"))
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, verbose_name=_("The longitude of the airport"))


class AirportAdmin(admin.ModelAdmin):
    pass


admin.site.register(Airport, AirportAdmin)
