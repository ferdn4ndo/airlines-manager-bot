from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _

from .airport_model import Airport
from .demand_model import Demand
from .generic_audited_model import GenericAuditedModel
from .price_model import Price


class Line(GenericAuditedModel):

    am_id = models.IntegerField(null=True, verbose_name=_("The ID of the line inside Airlines Manager"))
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("The line name"))
    base_duration = models.IntegerField(default=0, verbose_name=_("The base duration of the trip "))
    display_name = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("The line display name"))
    origin = models.ForeignKey(to=Airport, on_delete=models.SET_NULL, null=True, verbose_name=_("The origin airport (relation)"), related_name="origin_airport")
    destination = models.ForeignKey(to=Airport, on_delete=models.SET_NULL, null=True, verbose_name=_("The origin airport (relation)"), related_name="destination_airport")
    distance_km = models.IntegerField(default=0, null=True, verbose_name=_("The total distance of the line in kilometers"))
    total_demand = models.ForeignKey(to=Demand, on_delete=models.SET_NULL, null=True, verbose_name=_("The total demand (relation)"), related_name="total_demand")
    ideal_cost = models.ForeignKey(to=Price, on_delete=models.SET_NULL, null=True, verbose_name=_("The computed ideal cost (relation)"), related_name="ideal_cost_price")
    turnover = models.ForeignKey(to=Price, on_delete=models.SET_NULL, null=True, verbose_name=_("The turnover price (relation)"), related_name="turnover_price")
    current_cost = models.ForeignKey(to=Price, on_delete=models.SET_NULL, null=True, verbose_name=_("The current cost (relation)"), related_name="current_cost_price")
    internal_audit_cost = models.IntegerField(default=0, null=True, verbose_name=_("The cost of an internal audition of the ideal cost"))
    last_audit_date = models.DateField(null=True, verbose_name=_("The date when the ideal cost was last audited"))
    reliability_level = models.IntegerField(default=0, null=True, verbose_name=_("The reliability level (0 is the best, 10 is a bit unreliable)"))
    taxes = models.IntegerField(default=0, null=True, verbose_name=_("The cost of the taxes to fly an airplane in the line"))
    total_airplanes_assigned = models.IntegerField(default=0, verbose_name=_("The total number of airplanes with flights on this line"))
    total_weekly_flights = models.IntegerField(default=0, verbose_name=_("The total number of flights for this airport in the week"))
    can_update_prices = models.BooleanField(default=False, verbose_name=_("True when the line can have the prices audited (or false when in the cooldown)"))
    last_synced_at = models.DateTimeField(null=True, verbose_name=_("The date when the line data was last synced with the game servers"))

    def update_total_demand(self, economic: int, executive: int, first_class: int, cargo: int):
        if self.total_demand is None:
            self.total_demand = Demand()

        self.total_demand.economic = economic
        self.total_demand.executive = executive
        self.total_demand.first_class = first_class
        self.total_demand.cargo = cargo

        self.total_demand.save()

    def update_ideal_cost(self, economic: float, executive: float, first_class: float, cargo: float):
        if self.ideal_cost is None:
            self.ideal_cost = Price()

        self.ideal_cost.economic = economic
        self.ideal_cost.executive = executive
        self.ideal_cost.first_class = first_class
        self.ideal_cost.cargo = cargo

        self.ideal_cost.save()

    def update_turnover(self, economic: float, executive: float, first_class: float, cargo: float):
        if self.turnover is None:
            self.turnover = Price()

        self.turnover.economic = economic
        self.turnover.executive = executive
        self.turnover.first_class = first_class
        self.turnover.cargo = cargo

        self.turnover.save()

    def update_current_cost(self, economic: float, executive: float, first_class: float, cargo: float):
        if self.current_cost is None:
            self.current_cost = Price()

        self.current_cost.economic = economic
        self.current_cost.executive = executive
        self.current_cost.first_class = first_class
        self.current_cost.cargo = cargo

        self.current_cost.save()


class LineAdmin(admin.ModelAdmin):
    pass


admin.site.register(Line, LineAdmin)
