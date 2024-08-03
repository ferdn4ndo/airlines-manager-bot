from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _

from .hub_model import Hub
from .line_model import Line
from .generic_audited_model import GenericAuditedModel


class HubLine(GenericAuditedModel):

    hub = models.ForeignKey(to=Hub, on_delete=models.CASCADE, null=True, verbose_name=_("The hub that owns the line (relation)"), related_name="hub_line_hub")
    line = models.ForeignKey(to=Line, on_delete=models.CASCADE, null=True, verbose_name=_("The line that is owned by the hub (relation)"), related_name="hub_line_line")


class HubLineAdmin(admin.ModelAdmin):
    pass


admin.site.register(HubLine, HubLineAdmin)
