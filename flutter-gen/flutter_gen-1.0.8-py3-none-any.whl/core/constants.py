DART_TYPES_DEFAULT_VALUES = {
    'int': '0',
    'bool': 'false',
    'String': '""',
    'double': '0.0',
    'float': 'Float(0.0)',
    'date': 'DateTime()',
    'void': '()',
    'dynamic': 'null',
    'ValidationResult': 'ValidationResult.valid()'
}

DART_TYPES_MOCK_VALUES = {
    'Int': '1',
    'Bool': 'true',
    'String': '"foobar"',
    'Double': '1.0',
    'Float': 'Float(1.0)',
    'Date': 'DateTime()',
    'Void': '()',
    'dynamic': 'null',
    'ValidationResult': 'ValidationResult.valid()'
}

DART_TYPES = {
    'int',
    'bool',
    'String',
    'double',
    'float',
    'Date',
    'void',
    'dynamic',
    'ValidationResult'
}

CSS_METHOD = {
    'font-family': 'setFontFamily(FontFamily.%s)',
    'font-style': 'setFontStyle(FontStyle.%s)',
    'font-weight': 'setFontWeight(FontWeight.%s)',
    'font-size': 'setFontSize(%d)',
    'line-height': 'setLineHeight(%d)',
    'letter-spacing': 'setLetterSpacing(%f)',
    'text-transform': '%s()',
    'color': 'setColor(Color(0xff%s))',
}