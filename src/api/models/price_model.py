from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _

from .generic_audited_model import GenericAuditedModel


class Price(GenericAuditedModel):

    economic = models.FloatField(default=0.0, verbose_name=_("Price value for economic class passengers"))
    executive = models.FloatField(default=0.0, verbose_name=_("Price value for executive class passengers"))
    first_class = models.FloatField(default=0.0, verbose_name=_("Price value for first class class passengers"))
    cargo = models.FloatField(default=0.0, verbose_name=_("Price value for cargo"))


class PriceAdmin(admin.ModelAdmin):
    pass


admin.site.register(Price, PriceAdmin)
