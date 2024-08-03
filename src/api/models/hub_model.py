from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _

from .demand_model import Demand
from .airport_model import Airport
from .generic_audited_model import GenericAuditedModel


class Hub(GenericAuditedModel):

    am_id = models.IntegerField(null=True, verbose_name=_("The ID of the hub inside Airlines Manager"))
    airport = models.ForeignKey(to=Airport, on_delete=models.SET_NULL, null=True, verbose_name=_("The hub airport (relation)"), related_name="hub_airport")
    bought_at = models.DateTimeField(null=True, verbose_name=_("The date/time when the hub was bought"))
    total_yearly_pax = models.IntegerField(default=0, null=True, verbose_name=_("The total amount of passengers transported in one year"))
    max_category = models.IntegerField(default=0, null=True, verbose_name=_("The maximum category (1-10) of airplane that the hub can hold"))
    total_lines_km = models.IntegerField(default=0, null=True, verbose_name=_("The total amount of kilometers of lines (all summed)"))
    runaway_length = models.IntegerField(default=0, null=True, verbose_name=_("The biggest runaway length of the hub"))
    taxes = models.IntegerField(default=0, null=True, verbose_name=_("The cost of the taxes to fly an airplane in the hub"))
    weekly_turnover = models.IntegerField(default=0, null=True, verbose_name=_("The turnover value accumulated for 7 days in the hub"))
    weekly_fuel_cost = models.IntegerField(default=0, null=True, verbose_name=_("The fuel cost accumulated for 7 days in the hub"))
    weekly_taxes = models.IntegerField(default=0, null=True, verbose_name=_("The taxes accumulated for 7 days in the hub"))
    weekly_supplement = models.IntegerField(default=0, null=True, verbose_name=_("The supplement cost accumulated for 7 days in the hub"))
    weekly_revenue = models.IntegerField(default=0, null=True, verbose_name=_("The revenue accumulated for 7 days in the hub"))
    weekly_transported_demand = models.ForeignKey(to=Demand, on_delete=models.SET_NULL, null=True, verbose_name=_("The hub transported demand accumulated for 7 days"), related_name="hub_weekly_demand")
    monthly_incidents_count = models.IntegerField(default=0, null=True, verbose_name=_("The number of incidents that happened in the hub during the latest 30 days"))
    monthly_incidents_cost = models.IntegerField(default=0, null=True, verbose_name=_("The accumulated cost of the incidents that happened in the hub during the latest 30 days"))
    monthly_flights_cancelled = models.IntegerField(default=0, null=True, verbose_name=_("The number of flights cancelled due to incidents in the hub during the latest 30 days"))


class HubAdmin(admin.ModelAdmin):
    pass


admin.site.register(Hub, HubAdmin)
