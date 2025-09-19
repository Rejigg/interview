import math

RADIUS_OF_EARTH_IN_MILES = 3958.8 # Radius of Earth in miles

# Used for calculating the distance between two points
def haversine(lat1, lon1, lat2, lon2):

    # Need to convert the lat and lng from the database to floats inorder to use this
    lat1, lon1, lat2, lon2 = float(lat1), float(lon1), float(lat2), float(lon2)

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(delta_lambda/2)**2
    c = 2*math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return RADIUS_OF_EARTH_IN_MILES * c