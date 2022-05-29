# from config import *

import nltk
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('punkt')

from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from colour import Color
from difflib import get_close_matches


import re
from word2number import w2n


standard_values = {'default': {'color': ['navy blue', 'rose gold', 'off white']},
 'bag': {'Bag-Type': ['Shopper Bag',
   'Toiletry Bag',
   'Tote Bag',
   'Crossbody Bag',
   'Shoulder Bag',
   'Bucket Bag',
   'Baguette',
   'Fanny Pack',
   'Belt Bag',
   'Wristlet',
   'Wallet',
   'Clutch',
   'Athletic Bag',
   'Backpack',
   'Handbag',
   'Mobile Phone Bag',
   'Hobo Bag',
   'Bottle Bag',
   'Satchel Bag'],
  'Bag-Pattern': ['Geometric', 'Animal'],
  'Bag-Size': ['Palm Size', 'Mini', 'Medium', 'Large'],
  'Bag-Material': ['Fabric',
   'Leather',
   'Vinyl',
   'Nylon',
   'Mesh',
   'Straw',
   'Acrylic',
   'Rhinestone',
   'Suede',
   'Velvet',
   'Crystal',
   'Glitter',
   'Crochet',
   'Beads',
   'Recycled Materials',
   'Fur',
   'Rubber'],
  'Bag-Closure': ['Zip',
   'Magnetic Clasp',
   'Gathered Drawstring',
   'Button',
   'Turn Lock Clasp',
   'No Closure',
   'Hook and Loop',
   'Flap',
   'Twist Closure'],
  'Bag-Strap': ['Adjustable',
   'Detachable',
   'Wristlet',
   'Short',
   'Shoulder',
   'Crossbody',
   'Thin',
   'Standard Width',
   'Wide',
   'Chain',
   'Multi Way',
   'Beaded',
   'Strapless',
   'Cord'],
  'Bag-Details': ['Pleats',
   'Pocket',
   'Outside Pocket',
   'Inside Pocket',
   'Front Pocket',
   'Quilted',
   'Inner Compartment',
   'Studs',
   'Lined',
   'Buckle',
   'Metal Buckle',
   'Topstitching',
   'Matching Topstitching',
   'Outer Compartment',
   'Unlined',
   'Compartments',
   'Knot',
   'Embroidered',
   'Pouch',
   'Flap',
   'Embellished',
   'Tassel'],
  'Bag-Detail': ['Pleats',
   'Pocket',
   'Outside Pocket',
   'Inside Pocket',
   'Front Pocket',
   'Quilted',
   'Inner Compartment',
   'Studs',
   'Lined',
   'Buckle',
   'Metal Buckle',
   'Topstitching',
   'Matching Topstitching',
   'Outer Compartment',
   'Unlined',
   'Compartments',
   'Knot',
   'Embroidered',
   'Pouch',
   'Flap',
   'Embellished',
   'Tassel'],
  'Bag-Handle': ['Top Handle',
   'Wooden Handle',
   'Metal Handle',
   'Leather Handle',
   'Plastic Handle',
   'No Handle',
   'Two Handles',
   'Handles',
   'Rope Handles',
   'Detachable Strap',
   'Chain',
   'Inner Compartments'],
  'All-Department': ['Bags']},
 'belt': {'Belt-Pattern': ['Crocodile',
   'Leopard',
   'Solid',
   'Stripes',
   'Textured'],
  'Belt-Department': ['Belts'],
  'Belt-Material': ['Leather',
   'Plastic',
   'Velvet',
   'Elastic',
   'Fabric',
   'Metal',
   'Straw',
   'Suede',
   'Rhinestone',
   'Glitter',
   'Reflective'],
  'Belt-Width': ['Ultra Skinny', 'Skinny', 'Medium', 'Wide', 'Ultra Wide'],
  'Belt-Detail': ['Two Rows Of Eyelets',
   'Tassels',
   'Chain',
   'Straps',
   'Rings',
   'Chunky',
   'One Row Of Eyelets',
   'Eyelets',
   'Pearls'],
  'Belt-Type': ['Wrap Belt',
   'Corset Belt',
   'Skinny Belt',
   'Harness Belt',
   'Bow Knot Belt',
   'Double Dual Buckle Belt',
   'Embellished Belt',
   'No Buckle Belt',
   'Rope Belt',
   'Chain Belt',
   'Pants Chain',
   'Cowboy Belt',
   'Braided Belt',
   'Suspenders Belt',
   'Clear Belt',
   'Waist Belt',
   'Low Waist Belt',
   'Leather Belt',
   'Basic Buckle Belt',
   'Belt Set',
   'Classic Belt',
   'Metal Belt',
   'Woven Belt',
   'Braided Belt',
   'Body Chain',
   'None'],
  'Belt-Fastening-Buckle': ['No Buckle',
   'Animal Shape Buckle',
   'Brand Logo Buckle',
   'Statement Buckle',
   'Bamboo Buckle',
   'Slim Buckle',
   'Bow Knot',
   'Flower Buckle',
   'Metal Buckle',
   'Adjustable Buckle',
   'C Shape Buckle',
   'Dual Buckle',
   'Hook and Eye Closure',
   'Lobster Clasp Closure',
   'Regtangular Buckle',
   'Round Buckle',
   'Rhinestone Buckle',
   'Squar Buckle',
   'Slip In Buckle',
   'Toggle Clasp Buckle',
   'Circle Buckle',
   'Geometric Buckle',
   'Oval Buckle',
   'None']},
 'scarve': {'Scarf-Department': ['Scarves'],
  'Scarf-Detail': ['Frayed edges',
   'Soft touch',
   'Open sides',
   'Ribbed trim',
   'Lined',
   'Zip at the top',
   'Polo-neck',
   'Fringes',
   'Tassel'],
  'Scarf-Material': ['Cotton',
   'Chiffon',
   'Silk',
   'Satin',
   'Wool',
   'Cashmere',
   'Knit',
   'Linen',
   'Net',
   'Fleece',
   'Jersey',
   'Alpaca',
   'Polyester',
   'Viscose',
   'Mohair'],
  'Scarf-Type': ['Bandana',
   'Shawl',
   'Infinity Scarf',
   'Triangle Scarf',
   'Blanket Scarf',
   'Rectangular Scarf',
   'Poncho',
   'Neck',
   'Tube',
   'Cape',
   'Balaclava',
   'Collar',
   'Sport Hijab',
   'Swim Hijab',
   'Hijab',
   'Scarf Accessory',
   'Infinity Scarf',
   'Scarf'],
  'Scarf-Pattern': ['Chain',
   'Colorblock',
   'Geometric',
   'Floral',
   'Paisley',
   'Graphic',
   'Leopard',
   'Solid',
   'Plants',
   'Polka Dots',
   'Snake']},
 'jewelry': {'Jewelry-Department': ['Necklaces',
   'Bracelets',
   'Earrings',
   'Rings',
   'Anklets',
   'Piercing Jewelry',
   'Body Chains'],
  'Jewelry-Gemstone': ['Ruby',
   'Pearl',
   'Rose quartz',
   'Lapis',
   'Moonstone',
   'Emerald',
   'Sapphire',
   'Diamond',
   'Topaz',
   'Amethyst',
   'Faux Gem',
   'Stone'],
  'Jewelry-Fastening': ['Clasps',
   'Push-back',
   'Lobster Clasp',
   'Hook',
   'Push-back',
   'Trigger Clasp',
   'Adjustable',
   'Studs',
   'Toggle Clasp'],
  'Jewelry-Detail': ['Bead',
   'Sea Shell',
   'Astrological Sign',
   'Twisted',
   'Disc',
   'Butterfly',
   'Heart',
   'Sun',
   'Projection',
   'Circle',
   'Snake',
   'Moon',
   'Magnetic',
   'Glow In The Dark',
   'Yin & Yang',
   'Textured',
   'Star',
   'Nazar',
   'Charms',
   'Letter',
   'Coin',
   'Chain',
   'Flower',
   'round',
   'Ring',
   'Pendants',
   'Pearls'],
  'Jewelry-Material': ['Glass',
   'Acrylic',
   'Metal',
   'Copper',
   'Silver',
   'Gold',
   'Stainless Steel',
   'Pearl',
   'Bone',
   'Seeds and Nuts',
   'Threads',
   'Wood',
   'Stone',
   'Ceramic',
   'Rhinestones',
   'Resin',
   'Beads',
   'Alloy',
   'Leather',
   'Suede',
   'Sea Shells',
   'Sterling Silver',
   'Gold Plated',
   'Enamel',
   'Fabric',
   'Plastic',
   'Textile'],
  'jewelry-sizes': ['No Size'],
  'Jewelry-Style': ['Beach',
   'Boho',
   'Timeless',
   'Victorian',
   'Glamorous',
   'Oriental',
   'Matching',
   'Bridal',
   'Statement',
   'Minimal',
   'Bling',
   'Chunky',
   'Vintage',
   'Girly',
   'Trendy'],
  'Jewelry-Type': ['Chain Bracelets',
   'Chain Necklace',
   'Beaded Necklace',
   'Body Chain',
   'Bracelets',
   'Chain',
   'EARRINGS',
   'Choker',
   'Ring',
   'Earrings',
   'Hoop Earrings',
   'Ear Cuffs',
   'Dangle Earrings'],
  'Jewelry-Color-Tone': ['navy blue', 'rose gold', 'off white']},
 'clothing': {'Clothing-Department': ['Tops',
   'Jackets',
   'Dresses',
   'Jumpsuits',
   'Playsuits',
   'Pants',
   'Jeans',
   'Shorts',
   'Skirts',
   'Beachwear',
   'Sets'],
  'Clothing-Style-Occasion': ['Sporty',
   'Casual',
   'Sexy',
   'Modest',
   'Elegant',
   'Workwear',
   'Boho',
   'Minimalist',
   'Loungewear',
   'Party',
   'Sa7el Wear',
   'Trendy',
   'Artsy',
   'Tomboy',
   'Street Style',
   'Hijabi',
   'Vintage',
   'Basic',
   'Glamorous',
   'Statement',
   'Edgy',
   'Skater',
   'Night out',
   'Girly'],
  'Clothing-Fit': ['Tight', 'Fitted', 'Straight', 'Loose', 'Oversize'],
  'Clothing-Neckline': ['V Neck',
   'Round',
   'Surplice',
   'Collared',
   'High Neck',
   'Sweetheart',
   'Square',
   'Lapel',
   'Scoop',
   'Illusion',
   'Cut Out',
   'Choker',
   'Low Cut',
   'Draped',
   'Asymmetric',
   'Boat',
   'Gathered',
   'Ruffled',
   'Slot Collar',
   'Drawstring',
   'Hood',
   'Straight Cut'],
  'Clothing-Sleeve-Length': ['Below Elbow', 'Sleeveless', 'Cap'],
  'Clothing-Dress-Skirt-Length': ['Midi',
   'Ankle Length',
   'Maxi',
   'Train',
   'Hi Low'],
  'Clothing-Top-Length': ['Below Hips',
   'Knee Length',
   'Above Hips',
   'Waist Length'],
  'Clothing-Shoulder': ['Halterneck',
   'Strapless',
   'Spaghetti Straps',
   'Wide Straps',
   'Cut Out',
   'Padded',
   'One Shoulder',
   'Illusion',
   'Off Shoulder',
   'Thin Straps',
   'Adjustable Straps',
   'Drop Shoulder',
   'Straps',
   'Smocked',
   'Chain Straps',
   'Standard',
   'Cold Shoulder',
   'Pleated',
   'Ruffled',
   'Gathered',
   'Decorative',
   'Elastic'],
  'Clothing-Waistline': ['High',
   'Low',
   'Regular',
   'Elastic',
   'Drawstring',
   'Asymmetric',
   'Empire',
   'Dropped',
   'Fitted',
   'Gathered',
   'No Waist',
   'Draped',
   'Belted',
   'Waistband',
   'Ruffled',
   'Contrast'],
  'Clothing-Pants-Jeans-Length': ['Short Shorts',
   'Mid Thigh Shorts',
   'Knee Length Shorts',
   'Crop Pants',
   'Long Pants',
   'Extra long Pants'],
  'Clothing-Pants-Jeans-Leg-Style': ['Wide',
   'Loose',
   'Straight',
   'Boyfriend',
   'Mom',
   'Baggy',
   'Paperbag',
   'Skinny',
   'Cigarette',
   'Ultra Wide',
   'Stirrup',
   'Culottes',
   'Slim',
   'Flared',
   'Cargo',
   'Distressed'],
  'Clothing-Chest': ['Ruffled',
   'Open',
   'Knot',
   'Padded',
   'Lace',
   'Cut Out',
   'Sheer',
   'Embroidered',
   'Double Breasted',
   'Shaping Cups',
   'Wrapover',
   'Gathered',
   'Underwired',
   'Elastication',
   'Frill Trim',
   'Ties',
   'Corset'],
  'Clothing-Sleeve-Type': ['Regular',
   'Ballon',
   'Puff',
   'Raglan',
   'Layered',
   'Batwing',
   'Roll Up',
   'Split Sleeve',
   'Wide',
   'Straight',
   'Asymmetric',
   'Cuffed Sleeve'],
  'Clothing-Back': ['Open back',
   'Cut-Out',
   'Backless',
   'Illusion',
   'Crossover Ties',
   'Small Opening',
   'Ties',
   'Draping',
   'Low-cut',
   'Gathering',
   'Racer'],
  'Clothing-Denim-Wash': ['Light',
   'Dark',
   'Grey',
   'Medium',
   'Acid',
   'Colored',
   '90s wash',
   'Dirty wash',
   'Whiskers'],
  'Clothing-Pocket': ['Patch',
   'Front',
   'Welt',
   'False',
   'Back-Rear',
   'Chest',
   'Inseam',
   'Side',
   'No Pocket',
   'Zippered',
   'Cargo',
   'Kangaroo',
   'Draped',
   'Slash',
   'Jeans',
   'Flap',
   'Open',
   'Discreet'],
  'Clothing-Fabric-Elasticity': ['No Sretch',
   'Slight Stretch',
   'Medium Stretch',
   'High Stretch'],
  'Clothing-Lining': ['Unlined', 'Lined', 'Fully Lined'],
  'Clothing-Button': ['Side', 'Front'],
  'Clothing-Sleeve-Cuff': ['Cuffed',
   'Slits',
   'Elastic',
   'Buttoned',
   'Overlocked',
   'Wide',
   'Frill Trim',
   'Smocking'],
  'Clothing-Belted': ['Same Fabric',
   'Tied Belt',
   'Wide tie',
   'Detachable tie',
   'Ties'],
  'Clothing-Season': ['Summer', 'Winter', 'Fall', 'Spring', 'Sahel'],
  'Clothing-Material': ['Leather',
   'Viscose',
   'Cotton',
   'Woven',
   'Knit',
   'Polyester',
   'Suede',
   'Satin',
   'Silk',
   'Velvet',
   'Corduroy',
   'Gabardine',
   'Wool',
   'Crepe',
   'Chiffon',
   'Denim',
   'Fleece',
   'Velour',
   'Linen',
   'Tweed',
   'Fur',
   'Organza',
   'Nylon',
   'Mesh',
   '100% Cotton',
   'Alpaca',
   'Jersey',
   'Poplin',
   'Jacquard'],
  'Clothing-Fastening': ['Side',
   'Back',
   'Front',
   'Zip',
   'Invisible Zip',
   'Buttoned Front',
   'Back Zip',
   'Button and Metal Hook',
   'Front Zip Fly',
   'Double-Breasted',
   'Button',
   'Fake Fly',
   'Visible Zip',
   'Hook and eye'],
  'Clothing-Details': ['Cut-Out',
   'Tassel Drawstrings',
   'Trims',
   'Lace Trims',
   'Topstitching',
   'Pintucks',
   'Knot'],
  'Clothing-Ripped': ['Knee Ripped',
   'Destroyed',
   'Repaired',
   'One Knee Ripped',
   'Cut-out',
   'Ripped'],
  'Clothing-Ruffle': ['Ruffles', 'Shoulder'],
  'Clothing-Dart': ['Darted'],
  'Clothing-Pleat': ['Pleats', 'Back', 'Box'],
  'Clothing-Hemline': ['Slit',
   'Ruffled',
   'Flared',
   'Panelled',
   'Wrap',
   'Asymmetrical',
   'Mermaid',
   'Layered',
   'Overlocked',
   'Ribbed',
   'Rounded',
   'Cuffed',
   'Cut-off',
   'Vents',
   'PomPoms'],
  'Clothing-Type': ['Top',
   'Tunic',
   'T Shirt',
   'Bodysuit',
   'Sweater',
   'Crop Top',
   'Cami Top',
   'Tube Top',
   'Corset',
   'Sports Bra',
   'Hoodie',
   'Sweatshirt',
   'Blouse',
   'Polo Shirt',
   'Button Up Shirt',
   'Blazer',
   'Zip Up Hoodie',
   'Trench Coat',
   'Bomber Jacket',
   'Cardigan',
   'Baseball Jacket',
   'Coat',
   'Windbreaker',
   'Parka Coat',
   'Quilted Jacket',
   'Cape',
   'Vest',
   'Kimono',
   'Puffer Jacket',
   'Double Breasted Blazer',
   'Cape Blazer',
   'Bolero',
   'Overshirt',
   'Denim Jacket',
   'Leather Jacket',
   'Shirt Dress',
   'Bodycon Dress',
   'Blazer Dress',
   'T Shirt Dress',
   'Sun Dress',
   'Princess Dress',
   'Slip Dress',
   'Prom Dress',
   'Tent Dress',
   'Wrapped Dress',
   'Peasant Dress',
   'Kaftan',
   'A Line Dress',
   'Overall Dress',
   'Jumpsuit',
   'Active Jumpsuit',
   'Tailored Jumpsuit',
   'Cargo Jumpsuit',
   'Dungarees Jumpsuit',
   'Culottes Jumpsuit',
   'Overall Jumpsuit',
   'Ski Suit Jumpsuit',
   'Playsuit',
   'Wrap Playsuit',
   'Active Playsuit',
   'Dungarees Playsuit',
   'Tailored Playsuit',
   'Paperbag Pants',
   'Cargo Pants',
   'Jogger Pants',
   'Yoga Pants',
   'Leggings',
   'Harem',
   'Sweatpants',
   'Tailored Pants',
   'Culotte Pants',
   'Palazzo Pants',
   'Lounge Pants',
   'Bermuda Shorts',
   'Basketball Shorts',
   'Biker Shorts',
   'Sports Shorts',
   'Cargo Shorts',
   'Paperbag Shorts',
   'Hot Shorts',
   'Pompom Shorts',
   'Lounge Shorts',
   'Tailored Shorts',
   'Denim Shorts',
   'Skorts',
   'Wrap Skorts',
   'Denim Skorts',
   'Tailored Skorts',
   'Leather Shorts',
   'Leather Skorts',
   'Tennis Skirt',
   'Peasent Skirt',
   'Peplum Skirt',
   'Bodycon Skirt',
   'A Line Skirt',
   'Wrapped Skirt',
   'Circle Skirt',
   'Pencil Skirt',
   'Denim Skirt',
   'Skater Skirt',
   'Leather Skirt',
   'Flowy Skirt',
   'Beach Cover Up',
   'Bikini',
   'One Piece Swimsuit',
   'Burkini',
   'Tankini',
   'Athletic Swimsuit',
   'Bikini Top',
   'Bikini Bottom',
   'Tankini Top',
   'Tankini Bottom',
   'Co-ord',
   'Suit',
   'Set',
   'Sweatsuit']},
 'shoe': {'Shoe-Shoelace': ['Front'],
  'Shoe-Type': ['Slippers',
   'Sandals',
   'Boots',
   'Ankle Boots',
   'Cowboy Boots',
   'Sneakers',
   'Hi Top Sneakers',
   'Knee Boots',
   'Sock Boots',
   'Slingback',
   'Loafers',
   'Oxfords',
   'Mary Jane Shoes',
   'Thigh Boots',
   'Platform',
   'Pumps',
   'Court Shoes',
   'Mules',
   'Wedges',
   'Flip Flops',
   'Espadrilles',
   'Mid Calf Boots',
   'Gladiator Sandals',
   'Ballerina',
   'Army Boots',
   'Thong Sandals'],
  'Shoe-Material': ['Leather',
   'Fabric',
   'Vinyl',
   'Rhinestones',
   'Satin',
   'Mesh',
   'Straw',
   'Suede',
   'Glitter',
   'Velvet',
   'Shearling',
   'Nylon',
   'Fur',
   'Reflective',
   'Rubber'],
  'Shoe-Heel-Height': ['Flat',
   'Low',
   'Medium',
   'High',
   'Ultra High',
   'Platform'],
  'Shoe-Heel-Shape': ['Block',
   'Pyramid',
   'Stiletto',
   'Kitten',
   'Angular',
   'Chunky',
   'Wedge',
   'Cone',
   'Decorative',
   'Clear'],
  'Shoe-Strap': ['Wide',
   'Narrow',
   'Twisted',
   'Ankle',
   'Adjustable',
   'Foot',
   'Braided',
   'Padded',
   'Quilted',
   'Heel',
   'Crossover'],
  'Shoe-Insole': ['Leather',
   'Foam',
   'Padded',
   'Fleece',
   'Moulded',
   'Canvas',
   'Mesh',
   'Fabric',
   'Jersey',
   'Shearling',
   'Breathable'],
  'Shoe-Sole': ['Chunky',
   'Ribbed',
   'Rubber',
   'Patterned',
   'Angular',
   'Moulded',
   'Fluted'],
  'Shoe-Toe-Shape': ['Pointed',
   'Square',
   'Round',
   'Almond',
   'Peep',
   'Open',
   'Toe Post',
   'Vamp']}}

exclude_set = {'default': {'colour': None,
  'dark': None,
  'interior': None,
  'light': None,
  'straps': None,
  'ballet': None},
 'clothing': {'Clothing-Waistline': {'ballet': None},
  'Clothing-Composition': {'details': None, 'detail': None, ':': None}},
 'bag': None,
 'shoe': None,
 'jewelry': None,
 'belt': None,
 'scarve': None}


feature_group = {'default': None,
 'clothing': {'Clothing-Color': 'color'},
 'shoe': {'Shoe-Color': 'color'},
 'bag': {'Bag-Color': 'color'},
 'jewelry': {'Jewelry-Color-Tone': 'color'},
 'belt': {'Belt-Color': 'color'},
 'scarve': {'Scarf-Color': 'color'}}

no_join_features = {'color'}

con_map = {'default': {'transparent': 'clear',
  'greige': 'beige',
  'taper': 'almond',
  'chisel': 'almond',
  'cap': 'almond',
  'canvas': 'fabric',
  'twill': 'fabric',
  'cowl': 'draped',
  'crew': 'draped',
  'narrow': 'thin',
  'plush': 'velvet',
  'color': {'navy': 'navy blue',
   'rose': 'pink',
   'multicolor': 'multicolored',
   'ecru': 'beige',
   'mulberry': 'eggplant',
   'coffee': 'brown',
   'havan': 'brown',
   'burgundy': 'maroon',
   'prints': 'multicolored',
   'pearl': 'off white',
   'golden': 'gold'}},
 'clothing': {'trouser': 'pants',
  'trainers': 'sneakers',
  'palazzo': 'tailored',
  'formal': 'tailored',
  'jeggings': 'leggings',
  'relaxed': 'straight',
  'cowl': 'draped',
  'gathered': 'gather',
  'tie': 'choker',
  'vintage': 'wide',
  'tapered': 'cigarette',
  'velour': 'velvet',
  'strap': 'straps'},
 'bag': {'canvas': 'fabric',
  'cotton': 'fabric',
  'palazzo': 'tailored',
  'Bag-Closure': {'twist': 'twist closure'}},
 'shoe': {'slide': 'slippers',
  'sliders': 'slippers',
  'slides': 'slippers',
  'boot': 'boots',
  'methacrylate': 'clear',
  'perspex': 'clear',
  'strap': 'strappy',
  'cotton': 'fabric',
  'Shoe-Type': {'chelsea': 'ankle',
   'combat': 'ankle',
   'western': 'cowboy',
   'trainer': 'sneakers',
   'skate': 'sneakers',
   'running': 'sneakers',
   'flat': 'ballerina'},
  'Shoe-Heel-Height': {'mid': 'medium', 'short': 'low'}},
 'jewelry': {'closure': 'clasp',
  'transparent': 'clear',
  'greige': 'beige',
  'taper': 'almond',
  'chisel': 'almond',
  'cap': 'almond',
  'canvas': 'fabric',
  'twill': 'fabric',
  'cowl': 'draped',
  'crew': 'draped',
  'narrow': 'thin',
  'plush': 'velvet',
  'Jewelry-Color-Tone': {'navy': 'navy blue',
   'rose': 'pink',
   'multicolor': 'multicolored',
   'ecru': 'beige',
   'mulberry': 'eggplant',
   'coffee': 'brown',
   'havan': 'brown',
   'burgundy': 'maroon',
   'prints': 'multicolored',
   'pearl': 'off white',
   'golden': 'gold'}},
 'belt': {'geo': 'geometric',
  'Belt-Pattern': {'plain': 'solid'},
  'Belt-Type': {'pu': 'leather'},
  'Belt-Composition': {'pu': 'synthetic leather'}},
 'scarve': {'ecru': 'beige'}}


value_map = {'default': {'smartphone': 'mobile phone',
  'palazzo': 'tailored',
  'formal': 'tailored',
  'jeggings': 'leggings',
  'color': {'tiger havan': 'brown', 'only one': 'none'}},
 'shoe': {'Shoe-Heel-Height': {'kitten': 'low'},
  'high heel strappy': 'high',
  'tall boots': 'boots',
  'animal': 'animal Print',
  'unitard': 'active jumpsuit',
  'mid heel': 'medium',
  'hi top': 'high top sneakers',
  'Shoe-Type': {'slip on': 'Loafers',
   'wedge sandals': 'wedges',
   'ballet pump': 'Ballerina'}},
 'bag': {'adjustable shoulder': 'adjustable',
  'shopper': 'shopper bag',
  'short handle': 'short',
  'Bag-Detail': {'line': 'lined', 'external pocket': 'outside pocket'},
  'Bag-Details': {'line': 'lined', 'external pocket': 'outside pocket'},
  'Bag-Material': {'other': 'none'},
  'Bag-Size': {'s': 'small',
   'm': 'medium',
   'l': 'large',
   'o': 'none',
   'nosize': 'none',
   'onesizeL': 'none',
   'one size': 'none'},
  'Bag-Strap': {'Bead': 'Beaded'},
  'Bag-Type': {'crossbody': 'crossbody bag',
   'cross body': 'crossbody bag',
   'mobile bag': 'mobile phone bag',
   'smartphone bag': 'mobile phone bag',
   'tote': 'tote bag'},
  'Bag-Closure': {'magnetic': 'magnetic clasp',
   'zipper': 'zip',
   'zip closure': 'zip'}},
 'clothing': {'Clothing-Material': {'semi sheer': 'sheer'},
  'Clothing-Neckline': {'cowl neck': 'draped',
   'cowl neckline': 'draped',
   'deep': 'low cut',
   'high collar': 'high neck',
   'v neck dress': 'v neck',
   'v neck jumpsuit': 'v neck',
   'straight': 'square',
   'tie': 'choker',
   'wide': 'scoop',
   'collar': 'collared',
   'medium waist': 'regular'},
  'Clothing-Dress-Skirt-Length': {'calf length': 'midi',
   'long': 'maxi',
   'short': 'mini'},
  'Clothing-Lining': {'fully line': 'fully lined', 'line': 'lined'},
  'Clothing-Fit': {'loose fitted': 'loose', 'wide': 'loose'},
  'Clothing-Pants-Jeans-Leg-Style': {'taper': 'cigarette',
   'vintage': 'wide',
   'ankle': 'crop Pants',
   'crop': 'crop Pants',
   'ankle length': 'crop pants',
   'cropped': 'cropped Pants',
   'extra long': 'extra long pants',
   'full length masculine': 'long pants',
   'full length satin': 'long pants'},
  'Clothing-Pants-Jeans-Length': {'ankle length': 'crop pants',
   'ankle': 'crop pants',
   'crop': 'cropped pants',
   'extra long': 'extra long pants',
   'full length': 'long pants',
   'long': 'long pants',
   'short': 'short shorts'},
  'Clothing-Shoulder': {'drop': 'drop shoulder',
   'exposed': 'off shoulder',
   'pronounced': 'decorative',
   'drop shoulder longline': 'drop shoulder',
   'elastication': 'elastic',
   'spaghetti': 'Spaghetti straps',
   'wide': 'wide straps',
   'narrow': 'thin straps',
   'detachable': 'detachable straps',
   'thin': 'thin straps'},
  'Clothing-Sleeve-Length': {'3/4 length': 'below elbow'},
  'Clothing-Style-Occasion': {'tom boy': 'tomboy'},
  'Clothing-Top-Length': {'long': 'below hips',
   'regular': 'above hips',
   'short': 'waist length',
   'bell': 'cirlce skirt',
   'bell skirt': 'cirlce skirt'},
  'Clothing-Type': {'bell': 'circle skirt',
   'bell skirt': 'circle skirt',
   'bermuda': 'bermuda shorts',
   'biker': 'biker shorts',
   'culotte': 'culotte pants',
   'cycle': 'biker shorts',
   'cycle shorts': 'biker shorts',
   'cycle short': 'biker shorts',
   'jogger': 'jogger pants',
   'jumper': 'jumpsuit',
   'romper': 'playsuit',
   'unitard': 'active jumpsuit',
   'unitard jumpsuit': 'active jumpsuit',
   'boiler suit jumpsuit': 'boiler suit',
   'button up': 'button up shirt',
   'cycle biker short': 'biker shorts',
   'ski suit': 'ski suit jumpsuit'},
  'Clothing-Waistline': {'contrast waistband': 'waistband',
   'drawstring waistband': 'drawstring',
   'elastic waistband': 'elastic',
   'gather': 'gathered Waist',
   'fitted waist': 'fitted',
   'medium waist': 'regular',
   'regular waist': 'regular',
   'dropped waist': 'dropped',
   'high waist': 'high',
   'elasticated': 'elastic',
   'elastication': 'elastic',
   'elastic Waistband': 'elastic',
   'mid waist': 'regular',
   'drop': 'dropped',
   'mid rise': 'regular',
   'gathered': 'gathered waist'},
  'deep': 'low cut',
  'deep v neck': 'v neck',
  'high collar': 'high neck',
  'highneck': 'high neck',
  'johnny collar': 'collared',
  'plung neck': 'low cut',
  'regular collar': 'collared'},
 'jewelry': {'Jewelry-Fastening': {'lobster clasp fasten': 'lobster clasp',
   'push back': 'push back clasp'},
  'Jewelry-Size': {'nosize': 'none', 'os': 'none'},
  'Jewelry-Type': {'chain link necklace': 'chain bracelet',
   'chain link bracelet': 'chain bracelet',
   'hoop': 'Hoop Earrings'},
  'smartphone': 'mobile phone',
  'palazzo': 'tailored',
  'formal': 'tailored',
  'jeggings': 'leggings',
  'Jewelry-Color-Tone': {'tiger havan': 'brown', 'only one': 'none'}},
 'scarve': {'Scarf-Detail': {'soft': 'soft touch'},
  'Scarf-Type': {'tube': 'infinity scarf', 'square scarf': 'triangle scarf'},
  'Scarf-Dimensions': {'m l': 'none',
   'one size': 'none',
   'onesize': 'none',
   'xs s': 'none'},
  'Scarf-Composition': {'materials : certification': 'none',
   'outer shell : certification': 'none'}},
 'belt': {'Belt-Type': {'wrap': 'wrap belt',
   'corset': 'corset belt',
   'skinny': 'skinny belt',
   'harness': 'harness belt',
   'bow Knot': 'bow Knot belt',
   'double dual buckle': 'double dual buckle belt',
   'embellished': 'embellished belt',
   'no buckle': 'no buckle belt',
   'rope': 'rope belt',
   'chain': 'chain belt',
   'cowboy': 'cowboy belt',
   'braided': 'braided belt',
   'suspenders': 'suspenders belt',
   'clear': 'clear belt',
   'waist': 'waist belt',
   'low waist': 'low waist belt',
   'leather': 'leather belt',
   'braid leather': 'braided belt',
   'classic faux': 'classic belt',
   'dual': 'double dual buckle belt',
   'dual buckle': 'double dual buckle belt',
   'pu buckle belts': 'leather belt',
   'set': 'belt set',
   'trouser chain': 'pants chain',
   'waistband belt': 'waist belt',
   'belt': 'none',
   'plus size wide belt': 'none',
   'plus size': 'none'},
  'Belt-Fastening-Buckle': {'adjustable': 'adjustable bukcle',
   'bold buckle': 'statement buckle',
   'hook': 'hook and eye closure',
   'Lobster Clasp': 'lobster clasp closure',
   'buckle': 'none'},
  'belt-material': {'woven': 'fabric'},
  'Belt-Width': {'slim': 'skinny', 'wide belt': 'wide'}}}


skip_set = {'default': {'breasted': None,
  'gathered': None,
  'leggings': None,
  'pants': None,
  'quilted': None,
  'shorts': None,
  'tailored': None,
  'oxfords': None,
  'sandals': None,
  'pumps': None,
  'padded': None,
  'ribbed': None,
  'plated': None,
  'xs': None,
  'earrings': None,
  'cuffs': None,
  'rose': None,
  'edges': None,
  'sides': None,
  'dropped': None,
  'belted': None,
  'beaded': None},
 'clothing': {'pants': None, 'Clothing-Waistline': {'fitted': None}},
 'bag': None,
 'shoe': None,
 'jewelry': {'Jewelry-Size': {'os': None},
  'breasted': None,
  'gathered': None,
  'leggings': None,
  'pants': None,
  'quilted': None,
  'shorts': None,
  'tailored': None,
  'oxfords': None,
  'sandals': None,
  'pumps': None,
  'padded': None,
  'ribbed': None,
  'plated': None,
  'xs': None,
  'earrings': None,
  'cuffs': None,
  'rose': None,
  'edges': None,
  'sides': None,
  'dropped': None,
  'belted': None,
  'beaded': None},
 'belt': None,
 'scarve': None}

additional_colors = {'apricot', 'bronze', 'cream', 'havan', 'navy', 'off', 'rose'}


small_words = {'default': {'cm': None},
 'clothing': {'xxxxx': None, 'Clothing-Department': {'xxxxx': None}},
 'bag': None,
 'shoe': None,
 'jewelry': None,
 'belt': None,
 'scarve': None}


capital_words = {'default': {'xs': None, 'xs/s': None},
 'jewelry': {'xs/s': None, 'Jewelry-Size': {'xl': None}, 'xs': None},
 'bag': None,
 'shoe': None,
 'clothing': None,
 'belt': None,
 'scarve': None}

plural = {'default': {'platform': None,
  'wedge': None,
  'slipper': None,
  'loafer': None,
  'mule': None,
  'sneaker': None,
  'heel': None,
  'ring': None,
  'earring': None,
  'pant': None},
 'clothing': {'set': None, 'Clothing-Department': {'short': None}},
 'bag': None,
 'shoe': None,
 'jewelry': None,
 'belt': None,
 'scarve': None}

numeric_features = {'jewelry': ['Jewelry-Number-of-Pieces'],
 'belt': ['Belt-Number-of-Pieces'],
 'clothing': ['Clothing-Number-of-Pieces']}


sentence = {'default': None, 'all_care': ['all-care', 'all']}



class Helper:

    def get_key_using_val(self, dic1, val1):

        # getting the kay name from dic1 that has a value val1
        key_list = list(dic1.keys())
        val_list = list(dic1.values())
        position = val_list.index(val1)
        #         key_name =  key_list[position]
        #         dic2[key_name] = dic2.pop('color')
        return key_list[position]

    def _update_dictionary(self, dict1, dict2):
        dict1 = {} if not dict1 else dict1
        dict2 = {} if not dict2 else dict2
        if dict2 and dict1:
            dict2.update(dict1)
            return dict2

        elif dict2:
            return dict2
        else:
            return dict1

    def seperate_digits(self, tokens):
        for i in range(len(tokens)):
            if not self.is_num(tokens[i]):
                splitted = re.split(r'(\d+)', tokens[i])
                splitted = [s for s in splitted if s not in ['']]
                joined = ''
                for j in range(len(splitted)):
                    if j >= len(splitted) - 1:
                        joined += splitted[j]
                    elif splitted[j + 1][0].isalpha() and splitted[j + 1].lower() != 'x':
                        joined += splitted[j] + ' '
                    else:
                        joined += splitted[j]
                tokens[i] = joined.replace('. ', '.').replace(' .', '.').lower()
        return tokens

    def check_digit(self, text):

        try:
            w2n.word_to_num(text)
            return True
        except ValueError:
            return False

    def get_digits(self, tokens):
        digits = [re.findall(r'\d+', token)[0] for token in tokens if re.findall(r'\d+', token)]
        if not digits:
            digits = [str(w2n.word_to_num(token)) for token in tokens if self.check_digit(token)]
        return digits

    def get_dimensions(self, value):
        units = ['cm', 'inch']
        unit = [unit for unit in units if unit in value.lower()]
        try:
            unit = unit[0]
        except:
            unit = ''
        value = value.replace(',', '.')
        d = value.lower().split('x')
        if len(d) < 2:
            d = value.lower().split(' ')
        digits = []
        for index, i in enumerate(d):
            try:
                num = digits.append(re.search(r'[0-9\.]+', i).group())
            except:
                pass

            if index > 2:
                continue
        digits = [digit for digit in digits if digit not in ['.', '', ' ']][0:3]
        if not digits:
            return value

        return " X ".join([digit for digit in digits]) + ' ' + unit

    def is_num(self, text):
        try:
            float(text)
            return True
        except:
            return False

    def map_tokens(self, map_dict, feature_name, tokens):
        for i in range(len(tokens)):
            if map_dict.get(feature_name) and map_dict.get(feature_name).get(tokens[i].lower()):
                tokens[i] = map_dict.get(feature_name).get(tokens[i].lower())
            elif map_dict.get(tokens[i].lower()):
                tokens[i] = map_dict.get(tokens[i].lower())
        return tokens

    def map_value(self, map_dict, feature_name, value):

        if map_dict.get(feature_name) and map_dict.get(feature_name).get(value.lower()):
            value = map_dict.get(feature_name).get(value.lower()).title()
        elif map_dict.get(value.lower()):
            value = map_dict.get(value.lower()).title()
        return value


class DataQualityTransformer(Helper):

    def __init__(self, standard_values= standard_values, exclude_set=exclude_set, skip_set=skip_set, feature_group=feature_group, no_join_features=no_join_features,
                 con_map=con_map, value_map=value_map, additional_colors=additional_colors, small_words=small_words, capital_words=capital_words, plural=plural,
                 numeric_features=numeric_features, sentence= sentence, tag='clothing'):

        self.tag = tag
        # Lemmatizer
        self.wnl = WordNetLemmatizer()

        self.is_noun = lambda pos: pos[0] == 'N'
        self.is_verb = lambda pos: pos[0] == 'V'
        self.is_adjective = lambda pos: pos[0] == 'J'
        self.is_adverb = lambda pos: pos[0] == 'R'
        self.is_conjunction = lambda pos: pos == 'CC'
        self.excluded = lambda pos: pos == 'PDT'
        self.has_cd = lambda poss: any([pos[1] == 'CD' for pos in poss])

        self.WN_NOUN = 'n'
        self.WN_VERB = 'v'
        self.WN_ADJECTIVE = 'a'
        self.WN_ADJECTIVE_SATELLITE = 's'
        self.WN_ADVERB = 'r'

        self.feature_parser = {'default': self.feature_value_parser}
        self.no_join_features = no_join_features
        self.additional_colors = additional_colors
        self.numeric_features = numeric_features.get(tag, [])
        self.sentence = self._update_dictionary(sentence.get('default', []), sentence.get(tag, []))

        # works only on one token at a time with adding the default values
        self.feature_group = self._update_dictionary(feature_group.get('default', []), feature_group.get(tag, []))
        self.skip_set = self._update_dictionary(skip_set.get('default', []), skip_set.get(tag, []))
        self.exclude_set = self._update_dictionary(exclude_set.get('default', []), exclude_set.get(tag, []))
        self.plural = self._update_dictionary(plural.get('default', []), plural.get(tag, []))
        self.small_words = self._update_dictionary(small_words.get('default', []), small_words.get(tag, []))
        self.capital_words = self._update_dictionary(capital_words.get('default', []), capital_words.get(tag, []))

        color_feature_name = self.get_key_using_val(self.feature_group, 'color')
        # Normalization
        self.standard_values = self._update_dictionary(standard_values.get('default', []), standard_values.get(tag, []))
        self.standard_values[color_feature_name] = self.standard_values.pop('color')

        self.value_map = self._update_dictionary(value_map.get('default', []), value_map.get(tag, []))
        self.value_map[color_feature_name] = self.value_map.pop('color')

        self.con_map = self._update_dictionary(con_map.get('default', []), con_map.get(tag, []))
        self.con_map[color_feature_name] = self.con_map.pop('color')

    def feature_value_parser(self, feature_name, value):
        if self.standard_values.get(feature_name) and 'color' not in feature_name.lower():
            matches = get_close_matches(value.title(), self.standard_values[feature_name], 1, 0.5)

            if matches:
                return matches[0]
            else:
                matches = [get_close_matches(token.title(), self.standard_values[feature_name], 1, 0.65) for token in
                           word_tokenize(value)]
                matches = [match[0] for match in matches if match]
                if matches:
                    return matches[0]
        return value

    def check_color(self, color):
        try:
            if color.lower().strip() in self.additional_colors:
                return True
            Color(color)
            return True
        except ValueError:
            return False

    def get_lemma(self, word, pos, feature_name):
        lemma_word = word

        if 'color' in feature_name.lower() and not self.check_color(lemma_word.lower()):
            return ''
        if word.lower() in self.skip_set.get(feature_name, {}) or word.lower() in self.skip_set:
            return word
        if self.is_noun(pos):
            lemma_word = self.wnl.lemmatize(word.lower(), self.WN_NOUN)
            if lemma_word == word:
                lemma_word = self.wnl.lemmatize(word.lower(), self.WN_VERB)
        elif self.is_verb(pos):
            lemma_word = self.wnl.lemmatize(word.lower(), self.WN_VERB)
        elif self.is_adjective(pos):
            lemma_word = self.wnl.lemmatize(word.lower(), self.WN_ADJECTIVE)
        elif self.is_adverb(pos):
            lemma_word = self.wnl.lemmatize(word.lower(), self.WN_ADVERB)
        if lemma_word.lower() in self.exclude_set.get(feature_name, {}) or lemma_word.lower() in self.exclude_set:
            return ''
        return lemma_word

    def special_tokonizer(self, feature_name, featue_value):
        special_tokens = []
        if self.standard_values.get(feature_name):
            special_tokens = [token.lower() for token in self.standard_values.get(feature_name) if
                              token.lower() in featue_value.lower()]
        rest_of_values = re.sub("|".join(special_tokens), "", featue_value.lower()).split(" ")
        special_tokens = [token.title() for token in special_tokens if token != '']
        rest_of_values = [val.title() for val in rest_of_values if val != '']
        return special_tokens + rest_of_values

    def characters_cleaning(self, value):
        'remove any characters/ sepcial characters'
        value = value.replace('-', ' ')
        return value.replace(',', ' ')

    def tokenizing(self, feature_name, value):
        'return tokens after some processing'
        tokens = [token.lower() for token in word_tokenize(value)]
        # remove '.' for non difits
        tokens = [token.replace('.', '') if not token.replace('.', '', 1).isdigit() else token for token in tokens]
        # remove '/' for non digits and size feature name
        return [token.replace('/', ' ') if not (
                token.replace('/', '', 1).isdigit() or 'size' in feature_name.lower()) else token for token in
                tokens]

    def con_mapper(self, tokens, con_map):
        return [con_map.get(word.lower().strip(), word.strip()) for word in tokens]

    def lemmetize(self, feature_name, tokens, lemmetizer):
        words_pos = nltk.pos_tag(tokens)
        return [lemmetizer(word, pos, feature_name) for (word, pos) in words_pos if not self.excluded(pos)]

    def join_captelaize_nouns(self, tokens):
        words_pos = nltk.pos_tag(tokens)
        return ' '.join(
            [word.strip().title() if word != '' and not self.is_conjunction(pos) else word.strip() for (word, pos) in
             words_pos])

    def check_tokens(self, feature_name, value, small_words, plural, capital_words):
        for i in range(len(value)):
            tokens = word_tokenize(value[i])
            # check if there are any words should be small
            tokens = [token.lower() if token.lower() in small_words.get(feature_name,
                                                                        {}) or token.lower() in small_words else token
                      for token in tokens]
            # check if there are any words should be plural
            tokens = [token + 's' if token.lower() in plural.get(feature_name, {}) or token.lower() in plural else token
                      for token in tokens]
            # check if there are any words should be capital
            value[i] = ' '.join([token.upper() if token.lower() in capital_words.get(feature_name,
                                                                                     {}) or token.lower() in capital_words else token
                                 for token in tokens])
            value[i] = value[i].replace(" %", "%").replace(" /", "/").replace(" 路", ",")

        return value

    def clean(self, feature_name, featue_value, use_convert=False):
        # value processing
        value = self.characters_cleaning(featue_value)

        # extract domantions from 'dimensions' feature name
        value = self.get_dimensions(value) if 'dimensions' in feature_name.lower() else value

        # tokens processing
        tokens = self.tokenizing(feature_name, value)

        # seperate digits from text with white space
        tokens = self.seperate_digits(tokens)

        # Using con_map to one to one value maping
        tokens = self.map_tokens(self.con_map, feature_name, tokens)

        # extract num if feature in numeric_features
        tokens = self.get_digits(tokens) if feature_name in self.numeric_features else tokens

        lemmatized_words = self.lemmetize(feature_name, tokens, self.get_lemma)

        # Using con_map to one to one value maping again after lemmatization
        lemmatized_words = self.map_tokens(self.con_map, feature_name, lemmatized_words)

        # return original tokens if not lemmatized_words
        if not lemmatized_words:
            lemmatized_words = tokens

        value = self.join_captelaize_nouns(lemmatized_words)

        # mapping values using value_map
        value = self.map_value(self.value_map, feature_name, value)

        # standarize values using standard_values
        fparser = self.feature_parser.get(feature_name, self.feature_parser.get('default'))
        value = fparser(feature_name, value)

        # split value of multi o/p features using special_tokonizer
        if self.feature_group.get(feature_name) in self.no_join_features:
            value = list(set(self.special_tokonizer(feature_name, value)))

        # convert non list objects to list
        if type(value) != list:
            value = [value]

        value = self.check_tokens(feature_name, value, self.small_words, self.plural, self.capital_words)

        if feature_name.lower() in self.sentence:
            value = [val.capitalize() for val in value]
        return value

    def df_clean(self, row):
        return self.clean(row['Feature Name'], row['Feature Value'])
