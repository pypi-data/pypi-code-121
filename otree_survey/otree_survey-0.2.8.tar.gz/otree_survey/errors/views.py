from django.shortcuts import render

from .utils import get_participant_from_path_or_none, get_error_code


def handler404(request, exception, template_name="global/Error.html"):
    context = {
        "error_msgs": [
            f"Page not found: {request.path}",
        ]
    }
    return render(request, template_name, context=context, status=404)


def handler_maker(status):
    def handler(request, *args, template_name="global/Error.html"):
        participant = get_participant_from_path_or_none(request.path)
        context = {
            "error_msgs": [
                f"Error code: {get_error_code(participant)}",
            ],
            "status": status,
            "exception": args[0] if args else None,
        }
        return render(request, template_name, context=context, status=status)

    return handler


handler500 = handler_maker(500)
handler403 = handler_maker(403)
handler400 = handler_maker(400)
