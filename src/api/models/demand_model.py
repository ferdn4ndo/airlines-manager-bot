from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _

from .generic_audited_model import GenericAuditedModel


class Demand(GenericAuditedModel):

    economic = models.IntegerField(default=0, verbose_name=_("Demand value for economic class passengers"))
    executive = models.IntegerField(default=0, verbose_name=_("Demand value for executive class passengers"))
    first_class = models.IntegerField(default=0, verbose_name=_("Demand value for first class class passengers"))
    cargo = models.IntegerField(default=0, verbose_name=_("Demand value for cargo"))

    @property
    def total_pax(self) -> int:
        return self.economic + self.executive + self.first_class


class DemandAdmin(admin.ModelAdmin):
    pass


admin.site.register(Demand, DemandAdmin)
