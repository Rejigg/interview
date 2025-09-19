from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Business
from .serializers import BusinessSerializer

from .constants import RADIUS_MILES_OPTIONS
from .services.business_search_service import BusinessSearchService


class BusinessViewSet(viewsets.ModelViewSet):
    queryset = Business.objects.all().order_by("name")
    serializer_class = BusinessSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=["post", "get"], url_path="search")
    def search(self, request):
        results = []

        if request.method == "POST":
            locations = request.data.get("locations", [])
            search_text = request.data.get("text", "")
            search_radius = request.data.get("radius_miles")

            business_search_service = BusinessSearchService(
                queryset=self.queryset,
                search_text=search_text,
                search_radius=search_radius
            )

            unique_businesses = business_search_service.search_locations(locations)
            serializer = self.get_serializer(unique_businesses, many=True)
            results = serializer.data

        #TODO: Explain when a search radius was expanded
        return Response({"results": results}, status=status.HTTP_200_OK)
