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
                # Gets locations based on State
                if location.get("state") is not None:
                    # Assume always capital state code
                    businesses_from_state = self.queryset.filter(state=location.get("state")).filter(name__icontains=search_text)
                    serializer = self.get_serializer(businesses_from_state, many=True)
                    results.extend(serializer.data)

                # Get location based on cities


                # Get locations based on lat/long

        return Response({"results": [results]}, status=status.HTTP_200_OK)
