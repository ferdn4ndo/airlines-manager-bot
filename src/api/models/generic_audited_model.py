from django.db import models
from django.utils.translation import gettext_lazy as _

from .user_model import CustomUser
from .generic_model import GenericModel


class GenericAuditedModel(GenericModel):
    created_by = models.ForeignKey(
        to=CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_creator",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Record creation timestamp"))
    updated_by = models.ForeignKey(
        to=CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_editor",
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Record last update timestamp"), null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return '%s object (%s)' % (self.__class__.__name__, self.id)

    objects = models.Manager()
