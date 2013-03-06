"""Views for the ``object_events`` app."""
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.generic import ListView, RedirectView

from .models import ObjectEvent


def is_integer(mark_string):
    """Function to check if a supposed pk is an integer."""
    try:
        mark_id = int(mark_string)
    except ValueError:
        return False
    return mark_id


class ObjectEventsListView(ListView):
    """View to display a defined amount of notifications."""
    paginate_by = settings.OBJECT_EVENTS_PAGINATION_ITEMS

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super(ObjectEventsListView, self).dispatch(request, *args,
                                                          **kwargs)

    def get_queryset(self):
        return ObjectEvent.objects.filter(user=self.user)


class ObjectEventsMarkView(RedirectView):
    """View to mark a set of object events as read."""
    permanent = False

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.method == 'POST':
            raise Http404
        if request.POST.get('single_mark'):
            mark_id = is_integer(request.POST.get('single_mark'))
            if not mark_id:
                raise Http404
            try:
                event = ObjectEvent.objects.get(user=request.user, pk=mark_id)
            except ObjectEvent.DoesNotExist:
                raise Http404
            event.read_by_user = True
            event.save()
        elif request.POST.get('bulk_mark'):
            event_pks = request.POST.get('bulk_mark').split(',')
            event_pks = [is_integer(n) for n in event_pks]
            if event_pks:
                ObjectEvent.objects.filter(
                    pk__in=event_pks, user=request.user).update(
                        read_by_user=True)
        return super(ObjectEventsMarkView, self).dispatch(request, *args,
                                                          **kwargs)

    def get_redirect_url(self, **kwargs):
        return reverse('object_events_list')
