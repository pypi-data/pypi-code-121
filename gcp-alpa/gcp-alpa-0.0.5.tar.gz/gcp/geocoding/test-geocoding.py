import json

from GCPGeocoding import GCPGeocoding, latlng_valid, latlng_write_cache, latlng_read_cache

geocoding = GCPGeocoding(api_key='AIzaSyAIy2BqQXz0Ua4VuUUKMtUbiJxwijU06zQ')

INPUT_FILE = 'latlng.json'

with open(INPUT_FILE) as inf:
    d = json.load(inf)

i = 0
cache_miss = 0
for key in d['LocationLatitude'].keys():
    i += 1
    latitude = d['LocationLatitude'][key]
    longitude = d['LocationLongitude'][key]

    # print(latitude, longitude)
    # print(latlng_valid(latitude, longitude))

    # latlng_write_cache(latitude, longitude, {})
    # r = latlng_read_cache(latitude, longitude)
    '''
    if r is None:
        print(f"Cache miss: {latitude}, {longitude}")
        latlng_write_cache(latitude, longitude, {})
        cache_miss += 1
    '''
    r = geocoding.reverse(latitude, longitude)
    print(r.country, r.locality, r.neighborhood)

print(i)
print(cache_miss)