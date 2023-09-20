from django.http import JsonResponse
from .models import Presentation, Status
from common.json import ModelEncoder


class StatusEncoder(ModelEncoder):
    model = Status
    properties = ["name"]


class PresentationListEncoder(ModelEncoder):
    model = Presentation
    properties = [
        "title",
        "status"
    ]
    encoders = {
            "status": StatusEncoder(),
        }


class PresentationDetailEncoder(ModelEncoder):
    model = Presentation
    properties = [
        "presenter_name",
        "company_name",
        "presenter_email",
        "title",
        "synopsis",
        "created",
    ]


def api_list_presentations(request, conference_id):
    if request.method == "GET":
        presentations = Presentation.objects.filter(conference=conference_id)
        return JsonResponse(
            presentations,
            encoder=PresentationListEncoder,
            safe=False
        )


def api_show_presentation(request, id):
    """
    Returns the details for the Presentation model specified
    by the id parameter.

    This should return a dictionary with the presenter's name,
    their company name, the presenter's email, the title of
    the presentation, the synopsis of the presentation, when
    the presentation record was created, its status name, and
    a dictionary that has the conference name and its URL

    {
        "presenter_name": the name of the presenter,
        "company_name": the name of the presenter's company,
        "presenter_email": the email address of the presenter,
        "title": the title of the presentation,
        "synopsis": the synopsis for the presentation,
        "created": the date/time when the record was created,
        "status": the name of the status for the presentation,
        "conference": {
            "name": the name of the conference,
            "href": the URL to the conference,
        }
    }
    """
    presentation = Presentation.objects.get(id=id)
    return JsonResponse(
        presentation,
        encoder=PresentationDetailEncoder,
        safe=False,
    )
