from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render

from ood.models import ServerState
from ood.tasks import start as start_server
from ood.tasks import stop as stop_server


@login_required
def main(request):
    if request.user.is_authenticated and request.user.has_perm('ood.can_start'):
        server_state = ServerState.objects.get(id=1)
    else:
        server_state = None
    can_stop = request.user.has_perm('ood.can_stop')
    return render(request, 'main.html', {
        'server_state': server_state,
        'can_stop': can_stop,
    })


def logout(request):
    # The built-in logout auth view seems to always take me to the admin
    # logout page, so we call logout directly from our own view instead of
    # using the built-in view.
    # TODO: Figure out why it's overriding the return value here.
    auth_logout(request)
    return render(request, 'logout.html')


@login_required
@permission_required('ood.can_start')
def wakeup(request):
    start_server.delay()
    return redirect('processing_start')


@login_required
@permission_required('ood.can_stop')
def shutdown(request):
    stop_server.delay()
    return redirect('processing_stop')


# TODO: There should be just one processing_command view that takes a
# parameter in the path.
@login_required
def processing_start(request):
    server_state = ServerState.objects.get(id=1)
    if server_state.state == 'archived':
        return render(request, 'processing_command.html', {
            'processing_url': reverse('processing_start'),
            'command': 'start',
        })
    else:
        return redirect('main')


@login_required
def processing_stop(request):
    server_state = ServerState.objects.get(id=1)
    if server_state.state == 'running':
        return render(request, 'processing_command.html', {
            'processing_url': reverse('processing_stop'),
            'command': 'stop',
        })
    else:
        return redirect('main')
