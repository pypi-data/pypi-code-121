from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render


@login_required
@permission_required('indydash.view_dash')
def react_bootstrap(request):
    return render(request, 'indydash/react_base.html')
