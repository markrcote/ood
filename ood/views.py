from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render

from ood.forms import NewInstanceForm
from ood.models import DropletState, MineCraftServerSettings, OodInstance
from ood.states import droplet as droplet_states
from ood.tasks import start as start_server
from ood.tasks import stop as stop_server


@login_required
def main(request):
    can_start = request.user.has_perm('ood.can_start')
    can_stop = request.user.has_perm('ood.can_stop')

    if request.user.is_authenticated and can_start:
        instances = OodInstance.objects.all()
    else:
        instances = []

    return render(request, 'main.html', {
        'instances': instances,
        'can_start': can_start,
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
def wakeup(request, instance_id):
    start_server.delay(int(instance_id))
    return redirect(reverse('processing_start', args=(instance_id,)))


@login_required
@permission_required('ood.can_stop')
def shutdown(request, instance_id):
    stop_server.delay(int(instance_id))
    return redirect(reverse('processing_stop', args=(instance_id,)))


# TODO: There should be just one processing_command view that takes a
# parameter in the path.
@login_required
def processing_start(request, instance_id):
    instance = OodInstance.objects.get(pk=int(instance_id))
    if instance.state == 'archived':
        return render(request, 'processing_command.html', {
            'processing_url': reverse('processing_start', args=(instance_id,)),
            'command': 'start',
        })
    else:
        return redirect(reverse('main'))


@login_required
def processing_stop(request, instance_id):
    instance = OodInstance.objects.get(pk=int(instance_id))
    if instance.state == 'running':
        return render(request, 'processing_command.html', {
            'processing_url': reverse('processing_stop', args=(instance_id,)),
            'command': 'stop',
        })
    else:
        return redirect(reverse('main'))


@login_required
def new_instance(request):
    if request.method == 'POST':
        form = NewInstanceForm(request.POST)
        if form.is_valid():
            instance = OodInstance.objects.create(
                name=form.cleaned_data['name'],
                server_type=OodInstance.DROPLET_SERVER,
                state=droplet_states.Archived.name,
            )
            MineCraftServerSettings.objects.create(
                ood=instance,
                port=form.cleaned_data['port'],
                rcon_port=form.cleaned_data['rcon_port'],
                rcon_password=form.cleaned_data['rcon_password'],
            )
            DropletState.objects.create(
                ood=instance,
                name=form.cleaned_data['name'],
                region=form.cleaned_data['region'],
                pkey=form.cleaned_data['pkey'],
            )

            return redirect(reverse('main'))
    else:
        form = NewInstanceForm()

    return render(request, 'new_instance.html', {'form': form})
