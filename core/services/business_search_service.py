from ..constants import RADIUS_MILES_OPTIONS
from ..utils import haversine

class BusinessSearchService:
    def __init__(self, queryset, search_text, search_radius = RADIUS_MILES_OPTIONS[0]):
        self.queryset = queryset
        self.search_text = search_text
        self.search_radius = search_radius

    def filter_by_state(self, state: str):
        qs = self.queryset.filter(state=state).filter(name__icontains=self.search_text)

        return list(qs)

    # When a user enters city assume they also have a state so we can filter in that city and state
    # Assumes that the city would have been geocoded with Google geocoding API so we technically wouldn't need this
    def filter_by_city_state(self, city_state_str: str):
        # Split the city and state out to filter separately
        city, state = [part.strip() for part in city_state_str.split(",")]

        qs = (self.queryset.filter(city=city, state=state)
              .filter(name__icontains=self.search_text))

        return list(qs)

    # Ideally this is handled in SQL, sqlite doesn't allow for using haversine
    def filter_by_radius(self, lat: float, lng: float):
        # We could reduce our result set with a general bounding box, but we'd need to do a new query
        # each time we increase the search radius
        qs = self.queryset.filter(name__icontains=self.search_text)

        # Setting up for radius expansion if needed
        search_radii = [r for r in RADIUS_MILES_OPTIONS if r >= self.search_radius]
        if self.search_radius not in search_radii:
            search_radii = [self.search_radius] + search_radii

        for radius in search_radii:
            businesses_in_radius = [
                business for business in qs
                if haversine(lat, lng, business.latitude, business.longitude) <= radius
            ]

            # if we have a business within our radius then we don't need to expand, break
            if businesses_in_radius:
                return businesses_in_radius, radius  # Return first non-empty radius

        return []

    # Assumes that input is well-formed, otherwise we should be validating our inputs be
    def search_locations(self, locations):
        results = []
        expanded_radii_info = []

        for location in locations:
            # Retrieves locations based on state
            if location.get("state") is not None:
                results.extend(self.filter_by_state(location.get("state")))

            # Retrieves businesses based on city and state
            if location.get("city") is not None:
                results.extend(self.filter_by_city_state(location.get("city")))

            # Retrieves businesses based on lat/lon
            if location.get("lat") is not None and location.get("lng") is not None:
                lat, lng = float(location.get("lat")), float(location.get("lng"))
                businesses, expanded_radius = self.filter_by_radius(lat, lng)
                results.extend(businesses)

                # Record instances where the radius was expanded, return to front end with this data
                if expanded_radius != self.search_radius:
                    expanded_radii_info.append({
                        "lat": float(lat),
                        "lng": float(lng),
                        "radius": expanded_radius
                    })


        # Make unique list by ID
        unique_results = list({b.id: b for b in results}.values())
        return unique_results, expanded_radii_info