import json

INTERESTING_COMPONENTS = ['country', 'locality', 'neighborhood']

class GCPGeocodingResults():
    def __init__(self, results):
        self._results = results
        self._processed_results = {}
        self._process_results()

    def _process_results(self):
        for component in self._results:
            types = component['types']
            for int_component in INTERESTING_COMPONENTS:
                if int_component in types:
                    self._processed_results[int_component] = component['address_components']

    def _find_component_type(self, component_type):
        if component_type in self._processed_results.keys():
            r = self._processed_results[component_type]
            for x in r:
                if component_type in x['types']:
                    return x['long_name']
        return None

    @property
    def country(self):
        return self._find_component_type('country')

    @property
    def locality(self):
        return self._find_component_type('locality')

    @property
    def neighborhood(self):
        return self._find_component_type('neighborhood')

    @property
    def results(self):
        return self._results

    @property
    def processed_results(self):
        return self._processed_results


    @property
    def count(self):
        return len(self._results)

if __name__ == '__main__':
    with open('home.json') as inf:
        d = json.load(inf)

    if d['status'] == 'OK':
        r = GCPGeocodingResults(d['results'])

    # print(json.dumps(r.processed_results, indent=4))
    print(r.country)
    print(r.locality)
    print(r.neighborhood)