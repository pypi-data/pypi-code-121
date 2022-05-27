""" A utility for comparing tracking matrices """
import numpy as np

def matrices_equivalent(mat_a, mat_b, cube_length = 500.0, tolerance = 5.0):
    """
    Helper function to check the equivalence of 2 matrices.
    Because the 3x3 rotation and the 1X3 translation can
    have very different magnitudes we want something
    a bit more nuances than just np.allclose for the
    whole matrix.
    np.allclose worked OK until opencv-contrib-python > 4.5.1
    see Issue scikit-surgerybard Issue #69 and scikit-surgeryarucotracker
    issue #41

    Rather than comparing matrices let's look at what happens when we
    apply them to point cooridinates. If we define an operating cube,
    with the camera at the centre of the plane defined by the
    x and y axes and z = 0, by testing the differences at the
    extremities of that cube we can say that sksArucoTracker is accurate to
    within x mm over a volume of side length x mm. By default 5.0 mm and
    500 mm.

    This isn't very accurate but mainly seems to be due to
    instability in opencv-contrib-python. If you wanted more
    accuracy for a given application you could version
    lock opencv-contrib-python
    """
    cube_points = np.array(
                    [[-cube_length/2.0, -cube_length/2.0, cube_length, 1.],
                     [-cube_length/2.0, cube_length/2.0, cube_length, 1.],
                     [cube_length/2.0, cube_length/2.0, cube_length, 1.],
                     [cube_length/2.0, -cube_length/2.0, cube_length, 1.],
                     [-cube_length/2.0, -cube_length/2.0, 0., 1.],
                     [-cube_length/2.0, cube_length/2.0, 0., 1.],
                     [cube_length/2.0, cube_length/2.0, 0., 1.],
                     [cube_length/2.0, -cube_length/2.0, 0., 1.]],
                    dtype = np.float32)

    trans_a = np.matmul(mat_a, cube_points.transpose())
    trans_b = np.matmul(mat_b, cube_points.transpose())

    equivalent = np.allclose(trans_a, trans_b, rtol = 0.0, atol = tolerance)

    if not equivalent:
        print ("trans a: " , trans_a.transpose())
        print ("trans b: " , trans_b.transpose())
        print ("diff: " , trans_a.transpose() - trans_b.transpose())

    return equivalent
