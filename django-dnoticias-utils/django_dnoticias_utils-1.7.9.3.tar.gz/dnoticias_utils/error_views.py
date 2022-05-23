from django.shortcuts import render


def set_error_context(description, error_code):
    return {
        'error_code': error_code,
        'description': description,
    }


def handler_500(request):
    context = set_error_context("Upsss, houve um erro no pedido. Tente mais tarde.", 500)
    return render(request, "error.html", context=context, status=500)


def handler_404(request, exception):
    context = set_error_context("A página solicitada não foi encontrada.", 404)
    return render(request, "error.html", context=context, status=404)


def handler_403(request, exception):
    context = set_error_context("Eiii, esta página não é para ti!", 403)
    return render(request, "error.html", context=context, status=403)


def handler_400(request, exception):
    context = set_error_context("O servidor não conseguiu interpretar o seu pedido.", 400)
    return render(request, "error.html", context=context, status=400)
