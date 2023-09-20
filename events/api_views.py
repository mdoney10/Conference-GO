import json
from django.http import JsonResponse
from .models import Conference, Location, State
from common.json import ModelEncoder
from django.views.decorators.http import require_http_methods


class StateEncoder(ModelEncoder):
    model = State
    properties = [
        "abbreviation"
    ]


class LocationDetailEncoder(ModelEncoder):
    model = Location
    properties = [
        "name",
        "city",
        "room_count",
        "created",
        "updated",
        "state",
    ]
    encoders = {
            "state": StateEncoder(),
        }


class LocationListEncoder(ModelEncoder):
    model = Location
    properties = [
        "name",
        "state"
    ]
    encoders = {
            "state": StateEncoder(),
        }


class ConferenceDetailEncoder(ModelEncoder):
    model = Conference
    properties = [
        "name",
        "description",
        "max_presentations",
        "max_attendees",
        "starts",
        "ends",
        "created",
        "updated",
        "location",
    ]
    encoders = {
        "location": LocationListEncoder(),
    }


class ConferenceListEncoder(ModelEncoder):
    model = Conference
    properties = [
        "name"
    ]


def api_list_conferences(request):
    conferences = Conference.objects.all()
    return JsonResponse(
        {"conferences": conferences},
        encoder=ConferenceListEncoder,
    )


def api_show_conference(request, id):
    if request.method == "GET":
        conference = Conference.objects.get(id=id)
        return JsonResponse(
            conference,
            encoder=ConferenceDetailEncoder,
            safe=False,
        )
    else:
        content = json.loads(request.body)

    # Get the Location object and put it in the content dict
    try:
        location = Location.objects.get(id=content["location"])
        content["location"] = location
    except Location.DoesNotExist:
        return JsonResponse(
            {"message": "Invalid location id"},
            status=400,
        )

    conference = Conference.objects.create(**content)
    return JsonResponse(
        conference,
        encoder=ConferenceDetailEncoder,
        safe=False,
    )


@require_http_methods(["GET", "POST"])
def api_list_locations(request):
    if request.method == "GET":
        location = Location.objects.all()
        return JsonResponse(
            {"location": location},
            encoder=LocationDetailEncoder,
            safe=False
        )
    else:
        content = json.loads(request.body)
        state = State.objects.get(abbreviation=content["state"])
        content["state"] = state

        location = Location.objects.create(**content)
        return JsonResponse(
            location,
            encoder=LocationDetailEncoder,
            safe=False,
        )


@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_location(request, id):
    try:
        location = Location.objects.get(id=id)
    except Location.DoesNotExist:
        return JsonResponse(
            {"message": "Location not found"},
            status=404,
        )

    if request.method == "GET":
        return JsonResponse(
            location,
            encoder=LocationDetailEncoder,
            safe=False,
        )
    elif request.method == "PUT":
        content = json.loads(request.body)
        try:
            if "state" in content:
                state = State.objects.get(abbreviation=content["state"])
                content["state"] = state
        except State.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid state abbreviation"},
                status=400,
            )
        Location.objects.filter(id=id).update(**content)
        location = Location.objects.get(id=id)
        return JsonResponse(
            location,
            encoder=LocationDetailEncoder,
            safe=False,
        )
    elif request.method == "DELETE":
        location.delete()
        return JsonResponse({"message": "Location deleted"})
    else:
        return JsonResponse(
            {"message": "Unsupported method"},
            status=405,
        )
