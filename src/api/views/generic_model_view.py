from django.utils import timezone
from rest_framework import viewsets, mixins
from rest_framework.request import Request
from rest_framework.response import Response

from api.models import get_object_or_404


class GenericModelViewSet(viewsets.GenericViewSet):

    def get_object(self):
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj


class GenericModelCreateMixin(mixins.CreateModelMixin):

    def create(self, request: Request, *args, **kwargs) -> Response:
        request.data['created_at'] = timezone.now()
        request.data['created_by'] = request.user.id
        return super(GenericModelCreateMixin, self).create(request=request, *args, **kwargs)


class GenericModelUpdateMixin(mixins.UpdateModelMixin):

    def update(self, request: Request, *args, **kwargs) -> Response:
        request.data['updated_at'] = timezone.now()
        request.data['updated_by'] = request.user.id
        return super(GenericModelUpdateMixin, self).update(request=request, *args, **kwargs)


class FullCRUDListModelViewSet(GenericModelCreateMixin,
                               mixins.RetrieveModelMixin,
                               mixins.ListModelMixin,
                               GenericModelUpdateMixin,
                               mixins.DestroyModelMixin,
                               GenericModelViewSet):
    pass


class ReadUpdateDestroyModelViewSet(mixins.RetrieveModelMixin,
                                    mixins.ListModelMixin,
                                    GenericModelUpdateMixin,
                                    mixins.DestroyModelMixin,
                                    GenericModelViewSet):
    pass


class CreateReadModelViewSet(GenericModelCreateMixin,
                             mixins.RetrieveModelMixin,
                             mixins.ListModelMixin,
                             GenericModelViewSet):
    pass


class CreateModelViewSet(GenericModelCreateMixin,
                         GenericModelViewSet):
    pass


class ReadModelViewSet(mixins.RetrieveModelMixin,
                       mixins.ListModelMixin,
                       GenericModelViewSet):
    pass
