##    threadsnake. A tiny experimental server-side express-like library.
##    Copyright (C) 2022  Erick Fernando Mora Ramirez
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program.  If not, see <https://www.gnu.org/licenses/>.
##
##    mailto:erickfernandomoraramirez@gmail.com
    

import random
from typing import Any, Callable, List

Aggregator = Callable

class Generator:
    def __init__(self):
        pass
    
    def generate(self):
        pass
    
class ChoiceGenerator(Generator):
    def __init__(self, options:List[Any] = []):
        super().__init__()
        self.options = options
        
    def generate(self):
        if len(self.options) == 0:
            return None
        return random.choice(self.options)
    
class RangeGenerator(Generator):
    def __init__(self, maxValue: int = 255, minValue: int = 0):
        super().__init__() 
        self.maxValue = maxValue
        self.minValue = minValue
    
    def generate(self):
        return random.randint(self.minValue, self.maxValue)

class ComposedGenerator(Generator):
    def __init__(self, aggregator:Callable, generators:List[Generator] = []):
        self.aggregator = aggregator
        self.generators = generators
        super().__init__()
        
    def generate(self):
        return self.aggregator([g.generate() for g in self.generators])
    

class Style:
    def __init__(self, styleName:str, styleValue:str) -> None:
        self.styleName = styleName
        self.styleValue = styleValue
        
    def __str__(self):
        return f'\t{self.styleName}: {self.styleValue};'

class StyleRule:
    def __init__(self, selector:str, styles:List[Style] = []):
        self.selector = selector
        self.styles = styles

class StyleSheet:
    def __init__(self, styleRules:List[StyleRule] = []):
        self.styleRules = styleRules
        
    def __str__(self) -> str:
        result = ''
        for styleRule in self.styleRules:
            result += styleRule.selector + '{\n'
            for style in styleRule.styles:
                result += str(style) + '\n'
            result += '}\n\n'
        return result


def compose_color(function:str = 'rbg', components:List[int] = [0,0,0]):
    if len(components) <= 2:
        return 'black'
    else:
        return f'{function}({components[0]}, {components[1]}, {components[2]})'

def create_numeric_choice_generator(median:int = 127, delta:int = 10):
    return ChoiceGenerator([i for i in range(median-delta, median+delta)])
    
shortLinearGenerator = RangeGenerator()
shortLinearGenerators = [
    create_numeric_choice_generator(50, 20),
    create_numeric_choice_generator(130, 40),
    create_numeric_choice_generator(200, 20),
]

fonts = [
    'candara',
    '"times new roman"',
    'arial',
    '"century gothic"'
]

decorations = [
    'none'
]

rgbGenerator = ComposedGenerator(lambda x:compose_color('rgb', x), [random.choice(shortLinearGenerators) for i in range(3)])
lightRGBGenerator = ComposedGenerator(lambda x:compose_color('rgb', x), [shortLinearGenerators[0] for i in range(3)])
intenseRGBGenerator = ComposedGenerator(lambda x:compose_color('rgb', x), [shortLinearGenerators[2] for i in range(3)])
fontGenerator = ChoiceGenerator(fonts)



styles = {
    'color': intenseRGBGenerator,
    'background': lightRGBGenerator,
    'font-family': fontGenerator,
    'text-decoration': ChoiceGenerator(decorations)
}

def random_style(selector:str):
    global styles
    styles = [Style(i, styles[i].generate()) for i in styles]
    return StyleRule(selector, styles)

def random_stylesheet(selectors:List[str] = []):
    styleRules = [random_style(selector) for selector in selectors]
    return StyleSheet(styleRules)