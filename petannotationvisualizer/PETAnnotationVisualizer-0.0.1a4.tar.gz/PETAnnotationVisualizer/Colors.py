import numpy as np

# =============================================================================
# COLORS
# =============================================================================

Null_Color = 'ghost white'

# old, no more used. 
# Annotator_Colors = {
#             'Patrizio':'blue',
#             'Han': 'black',
#             'Chiara': 'purple',
#             'Mauro': 'red',
#             'Simone': 'orange'}
# the new implementation
# taken from http://www.science.smith.edu/dftwiki/index.php/Color_Charts_for_TKinter
MARK_COLORS = {
    'Activity': 'dark green',
    'AND Gateway': 'orange',
    'XOR Gateway': 'red',
    'Activity Data': 'dark salmon',
    'Actor': 'royal blue',
    'Condition Specification': 'gold4',
    'Further Specification': 'medium orchid',

    'Sequence Flow': 'green',
    'Uses': 'dark salmon',
    'Roles': 'blue',

    'Same Gateway': 'red',

    'Activity Data coref mention': 'gold',
    'Actor coref mention': 'azure',
}

PRECISION = 'orange'
RECALL = 'green'
F1SCORE = 'blue'

Annotator_Colors = {
    k:color for k, color in enumerate([ 'dark slate gray', 'dim gray', 'slate gray',
    'light slate gray', 'gray',  'midnight blue', 'navy', 'cornflower blue', 'dark slate blue',
    'slate blue', 'medium slate blue', 'light slate blue', 'medium blue', 'royal blue',  'blue',
    'dodger blue', 'deep sky blue', 'sky blue', 'light sky blue', 
    'dark turquoise', 'medium turquoise', 'turquoise',
    'cyan', 'cadet blue', 'medium aquamarine',  'dark green', 'dark olive green',
    'dark sea green', 'sea green', 'medium sea green', 'light sea green',
    'medium spring green', 'lime green', 'yellow green',
    'forest green', 'olive drab', 'dark khaki',
    'gold', 'goldenrod', 'dark goldenrod', 'rosy brown',
    'indian red', 'saddle brown', 'sandy brown',
    'dark salmon', 'salmon', 'light salmon', 'orange', 'dark orange',
    'coral', 'light coral', 'tomato', 'orange red', 'red', 'hot pink', 'deep pink',
    'pale violet red', 'maroon', 'medium violet red', 'violet red',
    'medium orchid', 'dark orchid', 'dark violet', 'blue violet', 'purple', 'medium purple',
    'snow4',
    'SlateBlue1', 'SlateBlue2', 'SlateBlue3',
    'SlateBlue4', 'RoyalBlue1', 'RoyalBlue2', 'RoyalBlue3', 'RoyalBlue4', 'blue2', 'blue4',
    'DodgerBlue2', 'DodgerBlue3', 'DodgerBlue4', 'SteelBlue1', 'SteelBlue2',
    'SteelBlue3', 'SteelBlue4', 'DeepSkyBlue2', 'DeepSkyBlue3', 'DeepSkyBlue4',
    'SkyBlue3', 'SkyBlue4',
    'turquoise4', 'cyan2', 'cyan3',
    'cyan4', 'DarkSlateGray4',
    'aquamarine2', 'aquamarine4',
    'DarkSeaGreen4', 'SeaGreen1', 'SeaGreen2', 'SeaGreen3', 'PaleGreen1', 'PaleGreen2',
    'PaleGreen3', 'PaleGreen4', 'SpringGreen2', 'SpringGreen3', 'SpringGreen4',
    'green2', 'green3', 'green4', 'chartreuse2', 'chartreuse3', 'chartreuse4',
    'OliveDrab1', 'OliveDrab2', 'OliveDrab4', 'DarkOliveGreen1', 'DarkOliveGreen2',
    'DarkOliveGreen3', 'DarkOliveGreen4', 'khaki1', 'khaki2', 'khaki3', 'khaki4',
    'LightGoldenrod1', 'LightGoldenrod2', 'LightGoldenrod3', 'LightGoldenrod4',
     'LightYellow4', 'yellow2', 'yellow3', 'yellow4',
    'gold2', 'gold3', 'gold4', 'goldenrod1', 'goldenrod2', 'goldenrod3', 'goldenrod4',
    'DarkGoldenrod1', 'DarkGoldenrod2', 'DarkGoldenrod3', 'DarkGoldenrod4',
     'RosyBrown3', 'RosyBrown4', 'IndianRed1', 'IndianRed2',
    'IndianRed3', 'IndianRed4', 'sienna1', 'sienna2', 'sienna3', 'sienna4',
                                        'burlywood4', 'wheat4', 'tan1',
    'tan2', 'tan4', 'chocolate1', 'chocolate2', 'chocolate3', 'firebrick1', 'firebrick2',
    'firebrick3', 'firebrick4', 'brown1', 'brown2', 'brown3', 'brown4', 'salmon1', 'salmon2',
    'salmon3', 'salmon4', 'LightSalmon2', 'LightSalmon3', 'LightSalmon4', 'orange2',
    'orange3', 'orange4', 'DarkOrange1', 'DarkOrange2', 'DarkOrange3', 'DarkOrange4',
    'coral1', 'coral2', 'coral3', 'coral4', 'tomato2', 'tomato3', 'tomato4', 'OrangeRed2',
    'OrangeRed3', 'OrangeRed4', 'red2', 'red3', 'red4', 'DeepPink2', 'DeepPink3', 'DeepPink4',
    'HotPink1', 'HotPink2', 'HotPink3', 'HotPink4', 'pink4',

    'PaleVioletRed2', 'PaleVioletRed3', 'PaleVioletRed4', 'maroon1', 'maroon2',
    'maroon3', 'maroon4', 'VioletRed1', 'VioletRed2', 'VioletRed3', 'VioletRed4',
    'magenta2', 'magenta3', 'magenta4', 'orchid1', 'orchid2', 'orchid3', 'orchid4',
                                        'MediumOrchid1', 'MediumOrchid2', 'MediumOrchid3',
    'MediumOrchid4', 'DarkOrchid1', 'DarkOrchid2', 'DarkOrchid3', 'DarkOrchid4',
    'purple1', 'purple2', 'purple3', 'purple4', 'MediumPurple1', 'MediumPurple2',
    'MediumPurple3', 'MediumPurple4',])
                                       }        

Sentence_Type_Colors = {
    # gold standard colors
    'Uninformative': 'red',
    'Process Relevant':'blue',
    'Process Model Relevant': 'green',
    
    'null':Null_Color
    }

Word_Type_Colors = {
    
    'Activity': 'blue',
    '': Null_Color
    }


Agreement_Scale_Full_20 = list([
    '#cd131a',
    '#d0290e',
    '#d23900',
    '#d34700',
    '#d35400',
    
    '#d26000',
    '#d16c00',
    '#ce7800',
    '#cb8300',
    '#c68e00',
    
    '#c19800',
    '#baa300',
    '#b3ad00',
    '#abb700',
    '#a1c100',
    
    '#96ca00',
    '#89d400',
    '#79dd00',
    '#65e617',
    '#49ef37'
    ])


Agreement_Scale_Full_5 = list([
    '#c40101',
    '#a34500',
    '#024872',
    '#4e6b00',
    '#027202',
    ])



Green_Scale_15 = list([  # Green # from light (poor Agreement) to dark (great agreement)
    '#68ef93',
    '#62ea8b',
    '#5ce482',
    '#57df7a',
    '#51d971',
    
    '#4bd469',
    '#46ce60',
    '#40c957',
    '#3ac34e',
    '#34be45',
    
    '#2eb93c',
    '#27b331',
    '#20ae26',
    '#18a81a',
    '#0da306',
    
    ])

Azure_Scale_15 = list([ # Azure/Blue # from light (poor Agreement) to dark (great agreement)
        '#7bdcff',
        '#5cd3ff',
        '#31c9ff',
        '#00bfff',
        '#00b5ff',
        
        '#00abff',
        '#00a0ff',
        '#0095ff',
        '#0089ff',
        '#007dff',
        
        '#0070ff',
        '#0062ff',
        '#0053f9',
        '#0041f1',
        '#182ae6',
    
    ])


Red_Scale_15 = list([ # RED # from light (poor Agreement) to dark (great agreement)
        '#f9d0d0',
        '#fac4c4',
        '#fbb9b7',
        '#fbadaa',
        '#faa19e',
        
        '#f99590',
        '#f78983',
        '#f57d76',
        '#f27168',
        '#ef645a',
        
        '#eb574d',
        '#e7493f',
        '#e23930',
        '#dd2721',
        '#d70810'
    ]) 

def GetAgreementColor(agreement, color_scale):
    len_scale = len(color_scale)
    
    scale = np.linspace(0.0, 1.0, num=len_scale, endpoint=True)
    
    
    # check first
    if agreement ==scale[0]: # == 0.0
        return color_scale[0]
    # check last
    if agreement ==scale[-1]:
        return color_scale[-1]
    for i in range(len_scale-1):
        # print(scale[i], scale[i+1])
        if agreement >= scale[i] and agreement < scale[i+1]:
            return color_scale[i]


if __name__ == '__main__':
        
    print(GetAgreementColor(0.08, Agreement_Scale_Full_20))