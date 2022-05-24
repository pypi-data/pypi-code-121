import unittest
from pypers.utils import img
from pypers.utils import utils
import subprocess
import shutil
import os


class MockSubprocess:

    last_return = None

    def get_return(self):
        return self.last_return

    def check_call(self, args):
        self.last_return = args

    def call(self, args):
        self.last_return = args


class Test(unittest.TestCase):

    def setUp(self):
        self.path = 'toto/foo/bar'
        try:
            shutil.rmtree('toto/')
        except Exception as e:
            pass
        os.makedirs(self.path)
        self.original_file = os.path.join(self.path, 'a.bmp')
        shutil.copy(os.path.join(os.path.dirname(__file__), 'files', 'a.bmp'),
                    self.original_file)
        self.large_file = os.path.join(self.path, 'b.png')
        shutil.copy(os.path.join(os.path.dirname(__file__), 'files', 'b.png'),
                    self.large_file)
        self.fade_large = os.path.join(self.path, 'c.png')
        shutil.copy(os.path.join(os.path.dirname(__file__), 'files', 'c.png'),
                    self.fade_large)
        for i in range(10):
            os.mkdir(os.path.join(self.path, '%s_f' % i))
            if i == 7:
                for j in range(10):
                    with open(os.path.join(self.path,
                                           '%s_f' % i,
                                           '%s.high.f_solr.xml' % j), 'w') as f:
                        f.write("test_file")
        self.mocker_suprocess = MockSubprocess()
        self.old_subprocess_check_call = subprocess.check_call
        self.old_subprocess_call = subprocess.call
        subprocess.check_call = self.mocker_suprocess.check_call
        subprocess.call = self.mocker_suprocess.call

    def tearDown(self):
        subprocess.check_call = self.old_subprocess_check_call
        subprocess.call = self.old_subprocess_call

        try:
            shutil.rmtree('toto/')
        except Exception as e:
            pass

    def test_analyse(self):
        if os.environ.get('SHORT_TEST', None):
            return
        img.Lire.analyse(['foo.jpg', "bar.jpg"])
        expected = ['/usr/bin/java', '-cp',
                    '/data/brand-data/lire/bin/commons-codec-1.9.jar:'
                    '/data/brand-data/lire/bin/common-image-3.0.jar:'
                    '/data/brand-data/lire/bin/common-io-3.0.jar:'
                    '/data/brand-data/lire/bin/common-lang-3.0.jar:'
                    '/data/brand-data/lire/bin/imageio-core-3.0.jar:'
                    '/data/brand-data/lire/bin/imageio-jpeg-3.0.jar:'
                    '/data/brand-data/lire/bin/imageio-metadata-3.0.jar:'
                    '/data/brand-data/lire/bin/imageio-tiff-3.0.jar:'
                    '/data/brand-data/lire/bin/jhlabs.jar:'
                    '/data/brand-data/lire/bin/lire-request-handler.jar',
                    'net.semanticmetadata.lire.solr.ParallelSolrIndexer',
                    '-n', '16', '-f', '-p', '-y', 'ce,sc', '-i',
                    ['foo.jpg', 'bar.jpg']]
        self.assertEqual(expected, self.mocker_suprocess.get_return())

    def test_rename(self):
        if os.environ.get('SHORT_TEST', None):
            return
        img.Lire.rename(self.path)
        res = os.listdir(os.path.join(self.path, '7_f'))
        expected = ["%s.lire.xml" % i for i in range(0, 10)]
        self.assertEqual(sorted(res), sorted(expected))

    def test_from_gif(self):
        if os.environ.get('SHORT_TEST', None):
            return
        gif_img = os.path.join(self.path, 'toto.gif')
        jpg_img = os.path.join(self.path, 'toto.jpg')
        with open(gif_img, 'w') as f:
            f.write('too')
        with open(jpg_img, 'w') as f:
            f.write('too')
        res = img.Convert.from_gif(jpg_img)
        self.assertEqual(res, jpg_img)
        self.assertTrue(os.path.exists(jpg_img))
        res = img.Convert.from_gif(gif_img)
        self.assertEqual(res, os.path.join(self.path, 'toto.png'))
        self.assertTrue(not os.path.exists(gif_img))
        convert_exe = utils.which('convert')
        expected = [convert_exe, '-resize', '512x512',
                    'toto/foo/bar/toto.gif', 'toto/foo/bar/toto.png']
        self.assertEqual(expected, self.mocker_suprocess.get_return())

    def test_to_hgh(self):
        if os.environ.get('SHORT_TEST', None):
            return
        res = img.Convert.to_hgh(self.original_file, 'test')
        self.assertEqual(res, os.path.join(self.path, 'test.png'))
        self.assertTrue(os.path.exists(res))
        self.assertTrue(os.path.exists(self.original_file))
        res = img.Convert.to_hgh(self.original_file, 'test')
        self.assertEqual(res, os.path.join(self.path, 'test.png'))
        res = img.Convert.to_hgh(os.path.join(self.path, 'test.png'), 'test')
        self.assertEqual(res, os.path.join(self.path, 'test.png'))

    def test_to_base64(self):
        if os.environ.get('SHORT_TEST', None):
            return
        expected = "/9j/4AAQSkZJRgABAgAAAQABAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFB" \
                   "QQEBQoHBwYIDAoMDAsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGB" \
                   "IUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQ" \
                   "UFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCABDAOYDASIA" \
                   "AhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAt" \
                   "RAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0" \
                   "KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFV" \
                   "WV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWm" \
                   "p6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8" \
                   "vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8" \
                   "QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEK" \
                   "RobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElK" \
                   "U1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmao" \
                   "qOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6O" \
                   "nq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD9U6KKKACiiigAooooAKKKKAC" \
                   "iiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoooo" \
                   "AKKKKACivw2/4Kx/Dfw18MP2jdA0/wAI+HtL8M6ddeFba6ntNJs0tYGl+" \
                   "1XabtifLu2RIP8AgFfpF+0r+zj8LNH/AGUviPBp/wAN/C9hDonhvV9R01" \
                   "4NHhR7O7+x/wDHxG6puWT/AEeDc/3m8pN33aAPqeivyG/4Iz/Dzwt4x1f" \
                   "4k6vrnhzS9b1bQZdGl0q61C0Sd7CVmum82It/q33RRfMvzfJR/wAFmPh5" \
                   "4W8Hav8ADbV9D8OaXomra9LrMuq3Wn2iQPfyq1q3mylf9Y+6WX5m+b56A" \
                   "P15or4l+FvwK+Bmrfs+/AnSfE/wu8N3useO9AsLAaha6PbxXTT/ANjPeS" \
                   "zvdJtlVttvL86tu3uv+9Xo3wJ/Zb0jw/8Asu2Xwd8c6Fb67pFhfapEtvq" \
                   "nl3Alt21K6ltZ9yfdd4nif5drpv8A4WoA+lKK/De48Aaf/wAE8P22tGPj" \
                   "bRLfxf4DeT7RYX2p2CTv9iZ/kni+Xb9qt2Vfu/3fl271r9O/iZ8DPhb+1" \
                   "rrOgarq/h3TfEGn6TLFdf29Ciq9+oV2isvNX5pYP3vmsu7Zu2r97fsAPo" \
                   "2ivmf9qn4GfDq3/ZU8eWkXgLw5Fb+GvC+sXuiLFpUCjTJfs7ytJb4X90z" \
                   "SorNt+9t+avh7/gjP8PPC3jHV/iTq+ueHNL1vVtBl0aXSrrULRJ3sJWa6" \
                   "bzYi3+rfdFF8y/N8lAH680V+G3/BWP4b+Gvhh+0boGn+EfD2l+GdOuvCt" \
                   "tdT2mk2aWsDS/artN2xPl3bIkH/AACv02+JH7OH7PsNx4d8I6r8J/C0U3" \
                   "jK8n0i0l03QrW2liZLK4unbzY1R4vkt3G9Pm3Mn+8oB9J0V8J+JfiBdf8" \
                   "ABN79iPT9Ke3W98S2Gq6ppfh63vpFdbhZdSu5beeXyv4fsuyVk+T+58jf" \
                   "dzP2Dvhg/wC0f8JT8VfjbdD4qav4hvpXsLDxJEt1YWMMDPB+6tW/cIzOs" \
                   "vKIv/oVAH3/AEV+bn7eX9ufsTHwX8TvgxfjwdpU96+kan4TtUP9j3LMHn" \
                   "R/sf8Aqot3lSq+xVb5vlZW3NX2V+zf8atP/aG+D/h7x7pkP2WPU4cXNpu" \
                   "LfZ7hG2TRbv4trI3zY+ZdtAHrNFfIv/BTL4ia14J/Zb8T2Xh60mu7/WYD" \
                   "ZXksX/LnpzOsVxO/+z+9SL/tvu/hrrP2Dvjqvx//AGafCuuXF39o1zTov" \
                   "7I1jeV3/aoFVd7f76bJf+B0AfR1FfPn7aXw38K+NP2c/iJqGu+G9L1i/w" \
                   "BE8Lavd6Vd31mksthKtq774Gb5om3xRfc/uLXwH/wR8+FPgr4of8LcHjL" \
                   "wfoHiv7F/ZP2X+2tMgvPs+/7bv8vzUbbu2L93+4tAH6/0V+SX7VnjXxD+" \
                   "xt+3D4N0z4RXWo2ugatp1jcT+C7a5Z7CdpbqWBreK3Z9kW5Yl27Nuxm+X" \
                   "bX2f+2v8CPA/wAVvh1a3Gv+HdOudZuNc8P6MuufZU+3wW0+tWsEsSXH31" \
                   "XbcS/Lu/jagD6eor8gP+CZvjXUv2cf2sPGXwR8VNJD/a88tgiuWVPt9rv" \
                   "ZHVG6LLFv+b+L91X6oeNZ2u7GDRoXdLjWZ/sW9B9yLaXnbP8AD+6R9rf3" \
                   "2SgDr6K/Db/gk58N/DXxP/aN1/T/ABd4e0vxNp1r4VubqC01azS6gWX7V" \
                   "aJu2P8ALu2SuP8AgdfuTQAUUUUAFFFFAH4r/wDBaf8A5Ok8K/8AYm2v/p" \
                   "be1+gP7Svws8S6T+zl8VLif4w+NdSt4PCurSSWV3Z6IkU6LZy/un8rTUb" \
                   "a33TtZW/uMtfPH7ZP7A/xx/a7+Ktl4wmbwB4WSz0iLSIrFNdvrvcqSyy7" \
                   "2k+wJ/FO38P8FfVPxU0L4y/FD4KeI/CS+GPA2n634j0m/wBFurhvFF69v" \
                   "BFNbrElwg/s3c7Zef8AdNt27E+d9zbAD4v/AOCGXT42/wDcE/8Ab+j/AI" \
                   "Lm9Pgl/wBxv/2wr1n9g/8AY/8AjF+x5rHiSG/PgjxHpHiSSwW8ltNcvIr" \
                   "izSB5dzxI1htlbbO/yMyfdX5lo/bw/Y/+MX7YeseG4bA+CPDmkeG5L9bO" \
                   "W71y8luLxJ3i2vKi2G2JtsCfIrP95vmagCl8JPhd4n07xP8AsVeM7jxxq" \
                   "2u6BLof2OLRNQhgSLTpZfDdxKgg8iKLcmyF0/e73+Vfnb5q+9or6zOo3G" \
                   "npKjXsEcVxLF/dVy6o3/kJ/wDvmvAvhhonx2+Gvwk8KeDIfCfw+vp/D+k" \
                   "WukRai/i++RZfIiSJZTF/Zf8Asfd31m/DDwH+0D4I8LeN9a1yfwH4p+JX" \
                   "iXWvtaH+07y10qws0tUiiRP9FaX5XRv3Xy/eZvN3M1AFb9uz9ni1/aj+G" \
                   "j+DtLtLe48aadnVNMvpn2JZHn5JW/uz7fKVfbf/AMsq+bv+CVf7UV1p81" \
                   "7+z946Z7DWNJnn/sP7Q+Jdyu32iyf/AGkbc6/8D/u19q/s+6J8UvD+hXd" \
                   "l8UbXwxc6nLJLdS634c1O6la8lZ/4reWBPK2JtVdsjfd+6tfHv7Tn/BP7" \
                   "4vfF39oub4o+ArnwV4Bmikie3uE1e8a7nuInbZey7bLbFKyeVuRdy/L99" \
                   "/vUAfaX7WP/ACa38Yv+xN1n/wBIpa+Af+CGXT42/wDcE/8Ab+vr7x94Z+" \
                   "PXj74Aa14N1LRPh/8A8JRr2kXmjahqsWv30doiywLF9oji+wMxZt8v7rc" \
                   "u3YnzPu2p41+wf+x/8Yv2PNY8SQ358EeI9I8SSWC3ktprl5FcWaQPLueJ" \
                   "GsNsrbZ3+RmT7q/MtAHyn/wWn/5Ok8K/9iba/wDpbe19s+OPg94w8M/ti" \
                   "fAPxXqfxF1vxr4d+2atpP2TW47WJ7K6fSbyVHRbW3iibekT/eXcNi/e3f" \
                   "L5B+2T+wP8cf2u/irZeMJm8AeFks9Ii0iKxTXb673Kkssu9pPsCfxTt/D" \
                   "/AAV9++Brnxdd6UZvGekaPpGriXYYtC1OW/tmTavz75beBlbdu+Ta38Pz" \
                   "N/CAfA//AAWl8G6rqvwy+H/iS2knbR9J1O6tby3iRmTfPEnlSt/d2/Z3X" \
                   "/tr/wB9e6/8EuLhbj9h74dxhuYJdSjkB7N/aV03/sy19B/ET4faJ8TfB2" \
                   "r+FvEmnrqmi6pbva3VpISu5W/2lO5W/usv3a8B+Bv7NPjf9kqPXtF+Heu" \
                   "ad418F6jdfbbHw/4pnlsJdOlYKr7b2KKfcvy/d8hf/QmoA8o/4LUXEafs" \
                   "0eErZmzLJ4vglVP9lbK93f8Aoa113/BJ7wbqXhT9kfT7i7kmMeu6vd6ra" \
                   "Q3CMpig/dQLt/2WaBpf+2n/AAKtv4t/sc6v+1R498P6v8Ytct7bwloqsL" \
                   "bwT4ZlllilnfbveW9ZYmb7m35Ykbb/ABJ81es/Gnw/8SovAJ8P/Bm18Ma" \
                   "JfSWklnFqGq3stqmmLtVImggitZVkb733tirsX738IBwfiT4v/BH4h2Xx" \
                   "C0bxh8TvBtpb6zHceG5dOvfENrb3EFrF5sT7laXcrtK8r7vl+Xyv7tfCP" \
                   "/BLv4pf8KT/AGn/ABR8JbvXrHV/D3iB5bS0vbG48+1uL+2Z/JmiZGZdks" \
                   "Xm/wC9+6/u1+qfw0tvEtl4atrPxJoeheH7qzK2sFp4f1aa/thbqiqh3y2" \
                   "8DL0Zdm1vur8/934a/ak/YH+MHxx/aOt/ip4Pn8C+C9RsvszRTNrF1cXE" \
                   "9xbSt5N0/wDoG1H2LAu359vlfeagD7J/ax/5Nb+MX/Ym6z/6RS1+W3/BM" \
                   "jwn8QPFngT45P8ADLxvdeDfFtlbaW1jDDbWc9pezf6bsWfz4JWX7pVWiZ" \
                   "fv/Nu4r9E/iN4a+NnxH+A+u+DpvDfgW28Q+IdKvdGvr7/hI7z7LFHLbrE" \
                   "txGn9nbmbLy/um27NifO+5tviH7B/7H/xi/Y81jxJDfnwR4j0jxJJYLeS" \
                   "2muXkVxZpA8u54kaw2yttnf5GZPur8y0AeI/8E9Pi3pPiz9qLxJp/wAa9" \
                   "MTVfjS9zKum+I9YbdNBLAvlS6ekWfKidfnZPKT/AJ6r/cr9Ef2lP+Se6R" \
                   "/2OXhL/wBSLT6+Xv22f+Cemt/G34m6D8Svhfqmj+FvGlvKjahcalLLAlx" \
                   "LHt+z3StFE/71Nqr935vl/ufN6t4y8LftG+Nfh74d0K+0T4cnWLDUtJ1K" \
                   "+1b/AISS+8q8lsb23uvlg/s3915r26fxtt3NQB8Z/wDBWT4X3vwn+OHgX" \
                   "44+GIPs1zeTxLdXCIuxNRs9stu7/wC08Sf+S9foh8B/idY/H3w7pfxG09" \
                   "Wj0q802KC0ib7yytte65/2ZQsX+9bvXM/tD/AzWv2mf2bNd8E+I7bSdC8" \
                   "WX8JuLZ7HUJbqytr2KXfbv5726Ntfaqt+63Kruq7vvV1+l+Ddb+EPwh8O" \
                   "+FPhxpGj6pPottFp9vFrupy2Fv5SxY83fFb3DO2/b8m1d25vm/vAH5Xf8" \
                   "EWP+TpPFX/Ym3X/AKW2VftRX5o/sbfsD/HH9kT4q3vjCFvAHilLzSJdIl" \
                   "sX12+tNqvLFLvWT7A/8UC/w/x1+l1ABRRRQAUUUUAFFFFABRRRQAUUUUA" \
                   "FFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRR" \
                   "QAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFF" \
                   "FFABRRRQAUUUUAFFFFABRRRQB//2Q=="
        self.assertEqual(expected, img.to_base64(self.original_file))

    def test_high(self):
        if os.environ.get('SHORT_TEST', None):
            return
        # No change
        current = img.to_base64(self.original_file)
        img.Generate.high(self.original_file)
        high = img.to_base64(self.original_file)
        self.assertEqual(current, high)
        # With resize
        current = img.to_base64(self.large_file)
        img.Generate.high(self.large_file)
        high = img.to_base64(self.large_file)
        self.assertNotEqual(current, high)

    def test_thumbnail_icon(self):
        if os.environ.get('SHORT_TEST', None):
            return
        functions = {
            'th': img.Generate.thumbnail,
            'ic': img.Generate.icon
        }
        for type in functions.keys():
            res = functions[type](self.large_file, 'test')
            self.assertEqual(res, os.path.join(self.path,
                                               "test-%s.jpg" % type))
            self.assertTrue(os.path.exists(os.path.join(self.path,
                                                        "test-%s.jpg" % type)))
            res = functions[type](self.large_file, 'test')
            self.assertEqual(res, os.path.join(self.path, "test-%s.jpg" % type))
            res = functions[type](os.path.join(self.path, "test-%s.jpg" % type),
                                  'b')
            self.assertEqual(res, os.path.join(self.path, "b-%s.jpg" % type))

    def test_crop(self):
        if os.environ.get('SHORT_TEST', None):
            return
        image_crop = os.path.join(self.path, 'cropped.png')
        res = img.crop(self.large_file, image_crop)
        self.assertEqual(res, 0)
        res = img.crop("no_image", image_crop)
        self.assertEqual(res, 2)
        res = img.crop(self.fade_large, image_crop)
        self.assertEqual(res, -1)

    def test_compress(self):
        if os.environ.get('SHORT_TEST', None):
            return
        img.compress(self.large_file)
        expected = ['optipng', '-quiet', '-o2', 'toto/foo/bar/b.png']
        self.assertEqual(expected, self.mocker_suprocess.get_return())


if __name__ == "__main__":
    unittest.main()
