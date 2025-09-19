from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Business
from .serializers import BusinessSerializer

from .constants import RADIUS_MILES_OPTIONS


class BusinessViewSet(viewsets.ModelViewSet):
    queryset = Business.objects.all().order_by("name")
    serializer_class = BusinessSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=["post", "get"], url_path="search")
    def search(self, request):
        results = []

        if request.method == "POST":
            locations       = request.data.get("locations", [])
            search_text     = request.data.get("text", "")
            search_radius   = request.data.get("radius_miles", RADIUS_MILES_OPTIONS[0]) # if none is provided use the first one

            # Assumes that input is well-formed, otherwise we should be validating our inputs be
            for location in locations:
                # TODO: Would be good to find a way to combine the state and city lookups to filter on a city if we have one
                # Gets locations based on State
                if location.get("state") is not None:
                    # Assume always capital state code
                    businesses_from_state = self.queryset.filter(state=location.get("state")).filter(name__icontains=search_text)
                    serializer = self.get_serializer(businesses_from_state, many=True)
                    results.extend(serializer.data)

                # When a user enters city assume they also have a state so we can filter in that city and state
                # Assumes that the city would have been geocoded with Google geocoding API so we technically wouldn't need this
                if location.get("city") is not None:
                    city, state = [part.strip() for part in location.get("city").split(",")]

                    businesses_from_city_state = (self.queryset.filter(city=city)
                                            .filter(state=state)
                                            .filter(name__icontains=search_text))

                    serializer = self.get_serializer(businesses_from_city_state, many=True)
                    results.extend(serializer.data)

                # Get locations based on lat/long


        return Response({"results": [results]}, status=status.HTTP_200_OK)
