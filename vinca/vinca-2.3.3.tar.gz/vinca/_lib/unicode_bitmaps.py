from pathlib import Path

quads_to_unicode = {((0,0),
 (0,0)):' ',
((0,0),
 (0,1)):'▗',
((0,0),
 (1,0)):'▖',
((0,0),
 (1,1)):'▄',
((0,1),
 (0,0)):'▝',
((0,1),
 (0,1)):'▐',
((0,1),
 (1,0)):'▞',
((0,1),
 (1,1)):'▟',
((1,0),
 (0,0)):'▘',
((1,0),
 (0,1)):'▚',
((1,0),
 (1,0)):'▌',
((1,0),
 (1,1)):'▙',
((1,1),
 (0,0)):'▀',
((1,1),
 (0,1)):'▜',
((1,1),
 (1,0)):'▛',
((1,1),
 (1,1)):'█'}


class Bitmap(list):
        # def __init__(self, l):
        #       list.__init__(self, l)
        #       self.rows = len(self)
        #       self.cols = len(self[0])
        #       assert all((len(row) == self.cols for row in self))  # all rows of equal length

        @property
        def rows(self):
                return len(self)

        @property
        def cols(self):
                return len(self[0])

        @classmethod
        def from_PBM(cls, file_name):
                """Read a Portable BitMap file; The format of a pbm file is
                P4
                141 141
                lots of binary
                """
                lines = Path(file_name).read_bytes().splitlines()
                code, dimensions, content = lines
                width, height = dimensions.split()
                width, height = int(width), int(height)
                # bitmaps are stored in bytes
                # so the width must be rounded up to a multiple of 8 bits
                width = next((x for x in range(width, width+8) if x%8==0))
                # use format 0=8b to convert each byte to something like 01101111 as a string
                bits = (bit for byte in content for bit in format(byte, '0=8b'))
                # make this list of bits an array with the right dimensions
                l = [[int(next(bits)) for col in range(width)] for row in range(height)]
                return cls(l)


        def raw_print(self):
                for row in self:
                        print(''.join(row))
        

        @staticmethod
        def grouped_into_pairs(l):
                """
                >>> Bitmap.grouped_into_pairs([1,2,3,4,5,6])
                [(1, 2), (3, 4), (5, 6)]
                """
                return list(zip(l[::2], l[1::2]))

        @staticmethod
        def transposed(m):
                """
                >>> Bitmap.transposed([[1,2], [3,4]])
                [[1, 3], [2, 4]]
                """
                return [list(col) for col in zip(*m)]

        def has_even_rows_and_cols(self):
                """
                >>> Bitmap([[0,1,0,1],[1,1,0,1]]).has_even_rows_and_cols()
                True
                """
                return self.rows % 2 == 0 and self.cols % 2 == 0

        def group_quadrants(self):
                """
                >>> Bitmap([[0,1,0,1],[1,1,0,1]]).group_quadrants()
                [[((0, 1), (1, 1)), ((0, 1), (0, 1))]]
                """
                assert self.has_even_rows_and_cols()
                m = self
                m = [self.grouped_into_pairs(row) for row in m]
                m = self.transposed(m)
                m = [self.grouped_into_pairs(col) for col in m]
                m = self.transposed(m)
                return m

        def pad(self):
                """pad array so that we have even number of rows and cols"""
                if self.rows % 2: # odd number of rows
                        self.append([0]*self.cols)
                if self.cols % 2: # odd number of cols
                        m = self
                        m = self.transposed(m)
                        m.append([0]*self.rows)
                        m = self.transposed(m)
                        self[:] = m
                assert self.has_even_rows_and_cols()
                

        def to_unicode(self):
                """
                >>> Bitmap([[0,1,0,1],[1,1,0,1]]).to_unicode()
                '▟▐'
                """
                if not self.has_even_rows_and_cols():
                        self.pad()
                m = self.group_quadrants()
                m = [[quads_to_unicode[q] for q in row] for row in m]
                m = [''.join(row) for row in m]
                m = '\n'.join(m)
                return m


if __name__ == '__main__':
        import doctest
        doctest.testmod()

