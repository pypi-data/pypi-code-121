'''
This module contains openscad built-in defintions
'''


SCAD_VARS = ['PI', '$fa', '$fs', '$fn', '$t', '$vpr', '$vpt', '$vpd', '$children',
             '$preview']


class CustomArgDef:
    '''
    Class to represent the custom argument defitions of some
    built-in module and functions.
    '''

    def check_call(self, call):
        """
        All child classes should overwrite this to check that the call is valid
        """
        return NotImplemented

# Module name, number of args, number of kwargs
# Many need special treatment at a later date because they don't behave as standard
SCAD_MODS = [('union', 0, 0),
             ('difference', 0, 0),
             ('intersection', 0, 0),
             ('echo', 0, 0), # Can accept infinite number of args, and args after kwags
             ('render', 1, 0), # args: convexity
             ('children', 1, 1), # args: index
             ('assert', 2, 1), # args: condition, message
             ('circle', 1, 1), # Only accepts one arg but this can be r or d.
             ('square', 2, 2), # args: size, center
             ('polygon', 3, 2), # args: points, paths, convexity
             ('text', 9, 8), # args: text, size, font, halign, valign, spacing, direction, language, script
             ('import', 3, 2), #args: file, convexity, layer
             ('projection', 1, 1), #args: cut
             ('sphere', 1, 1), # Only accepts one arg but this can be r or d.
             ('cube', 2, 2), # args: size, center
             ('cylinder', 4, 4), #Args are h, r1, r2, center if given without keywords. However can also use r, d, d1, d2!
             ('polyhedron', 3, 1), # args: points, faces, convexity; Note: depreciated triangles may be used!
             ('linear_extrude', 6, 5),  # args: height, center, convexity, twist, slices, scale; Note: only height can be set without name due to openscad bug
             ('rotate_extrude', 2, 2), # args: angle, convexity
             ('surface', 4, 3), # args: file, center, invert, convexity
             ('translate', 1, 1), # args: v
             ('rotate', 2, 1), # args: a, v
             ('scale', 1, 1), # args: v
             ('resize', 2, 1), #args, newsize, auto
             ('mirror', 1, 1), # args: v
             ('multmatrix', 1, 0), # args: m
             ('color', 2, 1), # args: c, alpha
             ('offset', 2, 1), # Function can either have inputs "r" or "delta, chamfer".
             ('hull', 0, 0),
             ('minkowski', 0, 0)]

#NOTE Built-in scad functions seem to ignore keywords for their non-keyword args
SCAD_FUNCS = [('is_undef', 1, 0),
              ('is_bool', 1, 0),
              ('is_num', 1, 0),
              ('is_string', 1, 0),
              ('is_list', 1, 0),
              ('concat', 0, 0), # Can accept infinite number of args
              ('lookup', 2, 0),
              ('str', 0, 0),
              ('chr', 0, 0), # Can accept infinite number of args
              ('ord', 1, 0),
              ('search', 4, 2), # kwargs: mnum_returns_per_match, index_col_num
              ('version', 0, 0),
              ('version_num', 0, 0),
              ('parent_module', 1, 0),
              ('abs', 1, 0),
              ('sign', 1, 0),
              ('sin', 1, 0),
              ('cos', 1, 0),
              ('tan', 1, 0),
              ('acos', 1, 0),
              ('asin', 1, 0),
              ('atan', 1, 0),
              ('atan2', 0, 0),
              ('floor', 1, 0),
              ('round', 1, 0),
              ('ceil', 1, 0),
              ('ln', 1, 0),
              ('len', 1, 0),
              ('log', 1, 0),
              ('pow', 2, 0),
              ('sqrt', 1, 0),
              ('exp', 1, 0),
              ('rands', 4, 1), # karg=seed
              ('min', 0, 0), # Can accept infinite number of args, cant be empty
              ('max', 0, 0), # Can accept infinite number of args, cant be empty
              ('norm', 1, 0),
              ('cross', 2, 0)]
