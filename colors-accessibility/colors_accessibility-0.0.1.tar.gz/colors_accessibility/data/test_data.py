TEST_DATA = {
    'cast_to_type': {
        'incorrect_types': [None, 1, 'new'],
    },
    'color_space': {
        'correct': {
            'lower': 'rgb',
            'upper': 'RGB'
        },
        'incorrect': 'incorrect'
    },
    'contrasts': {
        'below': 2.5,
        'middle': 3.51,
        'above': 7.24
    },
    'dictionaries': {
        'to_update_dictionary': {
            'first': 'old',
            'second': 'old',
            'third': 'old'
        },
        'update_dictionary': {
            'first': 'new',
            'fourth': 'new',
            'fifth': 'new'
        },
        'result': {
            'first': 'old',
            'second': 'old',
            'third': 'old',
            'fourth': 'new',
            'fifth': 'new'
        }
    },
    'hex': {
        'correct': {
            'short': {
                'with_hash': '#1ad',
                'without_hash': '1ad'
            },
            'long': {
                'with_hash': '#11aadd',
                'without_hash': '11aadd'
            },
            'rgb_to_hex': '#3b1f58',
            'hsl_to_hex': '#3a1f58',
            'relative_luminance': 0.34089079470345807,
            'list': ['#1ad']
        },
        'incorrect': {
            'characters': '#hjk',
            'value_length': '#123b'
        },
        'length': {
            'correct': '#123',
            'incorrect': ['#123', '#234']
        },
        'empty': None,
        'dictionary': {
            'hex': '#11aadd'
        }
    },
    'hsl': {
        'correct': {
            'raw': [269, 0.479, 0.233],
            'processed': [269, 0.479, 0.233],
            'hex_to_hsl': [195.0, 0.86, 0.47],
            'rgb_to_hsl': [269.0, 0.48, 0.23],
            'rgb_to_hsl_equal': [0, 0, 0.39],
            'relative_luminance': 0.02584094215704819,
            'normalized_hue': [0.23, 0.48, 0.23],
            'normalized_hue_processed': [82.8, 0.48, 0.23]
        },
        'incorrect': {
            'negative': [-1, 2, 3],
            'exceeded_maximum': [361, 2, 3],
            'non_projectable': [1, 'new', None]
        },
        'empty': None,
        'length': {
            'correct': [1, 2, 3],
            'incorrect': [1, 2, 3, 4]
        },
        'dictionary': {
            'hue': 0.2323,
            'saturation': 0.12312,
            'lightness': 0.34796
        },
        'dictionary_processed': [83.628, 0.12312, 0.34796]
    },
    'numeric': {
        'correct_numbers': [1, 2, 3],
        'correct': [1, 2.0, '3'],
        'incorrect': ['a', None, '3,11,1'],
        'negative': [-1, -2, -3],
        'empty': None,
        'number_for_processing_hsl': {
            'input': 0,
            'output': 0.2292797666666667
        },
        'hex_from_decimal': '1b',
        'decimal_to_hex': 27,
        'to_expand': [0.6, 0.6, 0.6],
        'expanded': [153, 153, 153],
        'associate': {
            'arguments_values': {
                'a': 1,
                'b': 2,
                'c': 3
            },
            'arguments_names': ['first', 'second', 'third'],
            'expected_output': {
                'first': 'a',
                'second': 'b',
                'third': 'c'
            }
        },
        'to_normalize': {
            'single_to_normalize': 25,
            'single_normalized': 0.25,
            'multiple_to_normalize': [25, 50, 75],
            'multiple_normalized': [0.25, 0.5, 0.75],
            'multiple_mixed': [0.25, 50, 10, 0.01, 0.001],
            'multiple_mixed_normalized': [0.25, 0.5, 0.1, 0.01, 0.001],
            'normalize_factor': 100
        },
        'contrast': 5.133599893400995
    },
    'rgb': {
        'correct': {
            'raw': [0.23137254901960785, 0.12156862745098039, 0.34509803921568627],
            'processed': [59, 31, 88],
            'hex_to_rgb': [17, 170, 221],
            'hex_to_rgb_normalized': [0.06666666666666667, 0.6666666666666666, 0.8666666666666667],
            'hsl_to_rgb': [58, 31, 88],
            'hsl_to_rgb_normalized': [0.22745098039215686, 0.12156862745098039, 0.34509803921568627],
            'relative_luminance': 0.02614360347909661,
            'equal': [100, 100, 100]
        },
        'incorrect': {
            'negative': [-1, 2, 3],
            'exceeded_maximum': [256, 2, 3],
            'non_projectable': [1, 'new', None]
        },
        'empty': None,
        'length': {
            'correct': [1, 2, 3],
            'incorrect': [1, 2, 3, 4]
        },
        'dictionary': {
            'red': 255,
            'green': 210,
            'blue': 0.123
        }
    },
    'signature': {
        'color_to_change_foreground': 'foreground',
        'color_to_change_background': 'background',
        'parameter': 'luminance',
        'signature_values': {
            'single': 1,
            'multiple': {
                1: 1,
                2: 1
            }
        },
        'incremented_color': {
            'color_space': 'hsl',
            'color_values': [269.0, 0.48, 0.23],
            'background_color_values': [195.0, 0.86, 0.47]
        }
    },
    'wcag_requirements': {
        'single': {
            'below': {},
            'middle': {
                'large_aa': [[269.0, 0.48, 0.23]],
            },
            'above': {
                'large_aa': [[269.0, 0.48, 0.23]],
                'large_aaa': [[269.0, 0.48, 0.23]],
                'normal_aa': [[269.0, 0.48, 0.23]],
                'normal_aaa': [[269.0, 0.48, 0.23]],
            }
        },
        'multiple': {
            'below': {},
            'middle': {
                'large_aa': [[269.0, 0.48, 0.23], [195.0, 0.86, 0.47]],
            },
            'above': {
                'large_aa': [[269.0, 0.48, 0.23], [195.0, 0.86, 0.47]],
                'large_aaa': [[269.0, 0.48, 0.23], [195.0, 0.86, 0.47]],
                'normal_aa': [[269.0, 0.48, 0.23], [195.0, 0.86, 0.47]],
                'normal_aaa': [[269.0, 0.48, 0.23], [195.0, 0.86, 0.47]],
            }
        }
    },
}
