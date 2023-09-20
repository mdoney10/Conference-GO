import json
from django.http import JsonResponse
from .models import Attendee
from common.json import ModelEncoder
from events.models import Conference
from django.views.decorators.http import require_http_methods


class ConferenceEncoder(ModelEncoder):
    model = Conference
    properties = [
        "name"
    ]


class AttendeesDetailEncoder(ModelEncoder):
    model = Attendee
    properties = [
        "email",
        "name",
        "company_name",
        "created",
        "conference",
    ]
    encoders = {
            "conference": ConferenceEncoder(),
        }


class AttendeesListEncoder(ModelEncoder):
    model = Attendee
    properties = [
        "name",
    ]


@require_http_methods(["GET", "POST"])
def api_list_attendees(request, conference_id):
    if request.method == "GET":
        attendees = Attendee.objects.filter(conference=conference_id)
        return JsonResponse(
            {"attendees": attendees},
            encoder=AttendeesListEncoder,
        )
    else:
        content = json.loads(request.body)

    # Get the Conference object and put it in the content dict
        try:
            conference = Conference.objects.get(id=conference_id)
            content["conference"] = conference
        except Conference.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid conference id"},
                status=400,
            )

    attendee = Attendee.objects.create(**content)
    return JsonResponse(
        attendee,
        encoder=AttendeesDetailEncoder,
        safe=False,
    )


def api_show_attendee(request, id):
    """
    Returns the details for the Attendee model specified
    by the id parameter.

    This should return a dictionary with email, name,
    company name, created, and conference properties for
    the specified Attendee instance.

    {
        "email": the attendee's email,
        "name": the attendee's name,
        "company_name": the attendee's company's name,
        "created": the date/time when the record was created,
        "conference": {
            "name": the name of the conference,
            "href": the URL to the conference,
        }
    }
    """
    attendee = Attendee.objects.get(id=id)

    attendee_details = {
        "email": attendee.email,
        "name": attendee.name,
        "company_name": attendee.company_name,
        "created": attendee.created.isoformat(),
        "conference": {
            "name": attendee.conference.name,
            "href": f"/api/conferences/{attendee.conference.id}/",
        }
    }

    return JsonResponse(attendee_details)
