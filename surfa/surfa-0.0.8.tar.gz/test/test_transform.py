import unittest
import numpy as np
import surfa as sf


class test_affine(unittest.TestCase):

    def test_init(self):
        """
        TODOC
        """

        # TODO test init with source/target images and surfaces

        for ndim in (2, 3):
            eye = np.eye(ndim + 1)
            aff = sf.Affine(eye)
            self.assertTrue(aff.ndim == ndim)
            
            aff = sf.Affine(eye[:ndim, :], transform_space='image-to-world')
            self.assertTrue(aff.ndim == ndim)
            
            aff = sf.transform.identity(ndim=ndim)
            self.assertTrue(np.array_equal(aff.matrix, eye))

            aff = sf.transform.random_affine(ndim=ndim)

        # bad entries
        self.assertRaises(Exception, sf.Affine, np.eye(2))
        self.assertRaises(Exception, sf.Affine, np.eye(5))

    def test_equivalence(self):
        """
        Test that affine equivalence functions are doing the right thing. The combinations of space
        and geometry are nonsensical here, but it doesn't matter.
        """
        
        for ndim in (2, 3):

            source = sf.ImageGeometry(np.repeat(128, ndim))
            target = sf.ImageGeometry(np.repeat(128, ndim))

            a = sf.transform.random_affine(ndim=ndim, source=source, target=target, transform_space='image-to-world')
            b = sf.Affine(a.matrix.copy(), source=source, target=target, transform_space='image-to-world')
            self.assertTrue(sf.transform.affine_equal(a, b))

            b = sf.Affine(a.matrix.copy(), source=target, target=source, transform_space='image-to-world')
            # self.assertFalse(sf.transform.affine_equal(a, b))  # todo
            self.assertTrue(sf.transform.affine_equal(a, b, matrix_only=True))

            b = sf.Affine(a.matrix.copy(), source=source, target=target, transform_space='surface-to-world')
            self.assertFalse(sf.transform.affine_equal(a, b))

            b = sf.Affine(a.matrix.copy() + 1e-5, source=source, target=target, transform_space='image-to-world')
            self.assertFalse(sf.transform.affine_equal(a, b, tol=0.9e-5))
            self.assertTrue(sf.transform.affine_equal(a, b, tol=1.1e-5))

    def test_point_transform(self):
        """
        todoc
        """
        # todo
        for ndim in (2, 3):

            affine = sf.transform.identity(ndim=ndim)

            moving = np.random.randn(ndim)
            moved = affine.transform(moving)
            # todo test difference

            moving = np.random.randn(5, ndim)
            moved = affine.transform(moving)
            # todo test diffference

            # TODO should we even support this?
            # moving = np.random.randn(5, 5, ndim)
            # moved = affine.transform(moving)
            # todo test diffference

            moving = np.random.randn(ndim + 1)
            self.assertRaises(Exception, affine.transform, moving)
            moving = np.random.randn(5, ndim + 1)
            self.assertRaises(Exception, affine.transform, moving)

            translation = np.random.randn(ndim)
            affine = sf.transform.compose_affine(translation=translation, ndim=ndim)
            moving = np.random.randn(ndim)
            moved = affine.transform(moving)
            true = moving + translation
            # todo add X and test differente

    def test_inverse(self):
        """
        Test affine matrix inversion. Important to test that source and target information is swapped
        in the resulting affine. The combinations of space and geometry are nonsensical here, but
        it doesn't matter.
        """

        for ndim in (2, 3):

            source = sf.ImageGeometry(np.repeat(128, ndim))
            target = sf.ImageGeometry(np.repeat(128, ndim))

            aff = sf.transform.identity(ndim, source=source, target=target, transform_space='image-to-world')
            inv = aff.inverse()

            self.assertTrue(aff.source is inv.target)
            self.assertTrue(aff.target is inv.source)
            self.assertTrue(aff.transform_space.source == inv.transform_space.target)
            self.assertTrue(aff.transform_space.target == inv.transform_space.source)
            self.assertTrue(np.array_equal(inv.matrix, np.linalg.inv(aff.matrix)))

    def test_matmul(self):
        """
        Test matrix multiplication of the affines. The important thing here is to make sure
        the source and target information is taken from the correct affines. The combinations
        of space and geometry are nonsensical here, but it doesn't matter.
        """
        for ndim in (2, 3):
            source = sf.ImageGeometry(np.repeat(128, ndim))
            target = sf.ImageGeometry(np.repeat(128, ndim))
            intermediate = sf.ImageGeometry(np.repeat(128, ndim))
            a = sf.transform.identity(ndim, source=intermediate, target=target, transform_space='world-to-surface')
            b = sf.transform.identity(ndim, source=source, target=intermediate, transform_space='image-to-world')
            c = a @ b
            self.assertTrue(sf.transform.geometry.image_geometry_equal(c.source, source))
            self.assertTrue(sf.transform.geometry.image_geometry_equal(c.target, target))
            self.assertTrue(c.transform_space == 'image-to-surface')

    def test_composition(self):
        """
        TODOC
        """

        for ndim in (2, 3):

            # identity (default) affine
            aff = sf.transform.compose_affine(ndim=ndim)
            self.assertTrue(np.array_equal(np.eye(ndim + 1), aff.matrix))
            translation, rotation, scale, shear = aff.decompose()
            self.assertTrue(np.all(translation == 0.0))
            self.assertTrue(np.all(rotation == 0.0))
            self.assertTrue(np.all(scale == 1.0))
            self.assertTrue(np.all(shear == 0.0))

            # random affine
            translation = np.random.uniform(-20, 20, ndim)
            rotation = np.random.uniform(-90, 90, 1 if ndim == 2 else 3)
            scale = np.random.uniform(0.5, 2.0, ndim)
            shear = np.random.uniform(-0.1, 0.1, 1 if ndim == 2 else 3)
            aff = sf.transform.compose_affine(translation, rotation, scale, shear, ndim=ndim)
            n_translation, n_rotation, n_scale, n_shear = aff.decompose()
            self.assertTrue(np.allclose(translation, n_translation))
            self.assertTrue(np.allclose(rotation, n_rotation))
            self.assertTrue(np.allclose(scale, n_scale))
            self.assertTrue(np.allclose(shear, n_shear))

            # radians
            rotation = np.radians(rotation)
            aff_radians = sf.transform.compose_affine(translation, rotation, scale, shear, ndim=ndim, degrees=False)
            self.assertTrue(np.array_equal(aff.matrix, aff_radians.matrix))
            n_translation, n_rotation, n_scale, n_shear = aff.decompose(degrees=False)
            self.assertTrue(np.allclose(translation, n_translation))
            self.assertTrue(np.allclose(rotation, n_rotation))
            self.assertTrue(np.allclose(scale, n_scale))
            self.assertTrue(np.allclose(shear, n_shear))


class test_space(unittest.TestCase):

    def test_init(self):
        """
        TODOC
        """

        # include some random capitalization
        good_names = [
            'i', 'image', 'IMG', 'vox', 'voxel',
            'W', 'RAS', 'world',
            'S', 'surf', 'surfACE',
        ]
        for name in good_names:
            space = sf.Space(name)

        # an unknown name
        self.assertRaises(Exception, sf.Space, None)
        self.assertRaises(Exception, sf.Space, 'bad')

    def test_equivalence(self):
        """
        TODOC
        """
        self.assertTrue(sf.Space('image') == sf.Space('voxel'))
        self.assertTrue(sf.Space('surface') == 's')
        self.assertTrue(sf.Space('world') == 'ras')
        self.assertFalse(sf.Space('world') == 'image')
        self.assertFalse(sf.Space('world') == None)


class test_image_geometry(unittest.TestCase):

    def test_init(self):
        """
        TODO
        """
        pass

    def test_update(self):
        """
        TODO
        """
        pass

    def test_writable(self):
        """
        TODO
        """
        pass

    def test_copy(self):
        """
        TODO
        """
        pass


class test_orientation(unittest.TestCase):

    def test_init(self):
        """
        TODO
        """
        pass


class test_deformation(unittest.TestCase):

    def test_init(self):
        """
        TODO
        """
        pass


if __name__ == '__main__':
    unittest.main()
