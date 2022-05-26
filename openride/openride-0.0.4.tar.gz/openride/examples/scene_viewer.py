from openride import Point, BoundingBox, Rotation, Size, Polygon, Polyline, Viewer



def main():

    v = Viewer()

    v.camera.set_position(Point(-5,0,1))
    v.draw_grid(delta=5)
    v.draw_grid(delta=1, alpha=0.3)

    point = Point()

    bounding_box = BoundingBox(
        position = Point(5, 4, 1),
        rotation = Rotation(0, 0, 1),
        size = Size(2, 1, 1)
    )

    polyline = Polyline([Point(x + 2, -3) for x in range(10)])

    polygon = Polygon([Point(7,1), Point(2,1), Point(3,-1), Point(7,-1, 0.3)])

    while True:
        v.draw_point(point)
        v.draw_bounding_box(bounding_box, color=(0,1,0), alpha = 0.75)
        v.draw_polyline(polyline, color = (1,0,1), linewidth = 3)
        v.draw_polygon(polygon, color = (1,0,0), alpha = 0.4)
        v.update()


if __name__ == "__main__":
    main()