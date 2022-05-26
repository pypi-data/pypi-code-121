from openride import Point, bird_eye_view_distance, Geometry
from shapely import geometry



def test_default_geometry_distance_from_shapely():

    class MockGeometry(Geometry):
        def to_shapely(self):
            return geometry.Point([1,1,1])
        def transform(self, transform):
            pass
    
    p1 = Point(0,0,0)
    p2 = MockGeometry()
    assert bird_eye_view_distance(p1, p2) == 2**0.5