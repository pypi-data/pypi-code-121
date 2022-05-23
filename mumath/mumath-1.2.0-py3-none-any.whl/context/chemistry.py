def normal(): return dict(mathvariant="normal")


_ELEMENTS = [
	(1, r"H", "Helium"),     # ^1H
    (1, r"D", "Deuterium"),  # ^2H
	(1, r"T", "Tritium"),    # ^3H
    (2, r"He", "Helium"),
    (3, r"Li", "Lithium"),
    (4, r"Be", "Beryllium"),
    (5, r"B", "Boron"),
    (6, r"C", "Carbon"),
    (7, r"N", "Nitrogen"),
    (8, r"O", "Oxygen"),
    (9, r"F", "Fluorine"),
    (10, r"Ne", "Neon"),
    (11, r"Na", "Sodium"),
    (12, r"Mg", "Magnesium"),
    (13, r"Al", "Aluminium"),
    (14, r"Si", "Silicon"),
    (15, r"P", "Phosphorus"),
    (16, r"S", "Sulfur"),
    (17, r"Cl", "Chlorine"),
    (18, r"Ar", "Argon"),
    (19, r"K", "Potassium"),
    (20, r"Ca", "Calcium"),
    (21, r"Sc", "Scandium"),
    (22, r"Ti", "Titanium"),
    (23, r"V", "Vanadium"),
    (24, r"Cr", "Chromium"),
    (25, r"Mn", "Manganese"),
    (26, r"Fe", "Iron"),
    (27, r"Co", "Cobalt"),
    (28, r"Ni", "Nickel"),
    (29, r"Cu", "Copper"),
    (30, r"Zn", "Zinc"),
    (31, r"Ga", "Gallium"),
    (32, r"Ge", "Germanium"),
    (33, r"As", "Arsenic"),
    (34, r"Se", "Selenium"),
    (35, r"Br", "Bromine"),
    (36, r"Kr", "Krypton"),
    (37, r"Rb", "Rubidium"),
    (38, r"Sr", "Strontium"),
    (39, r"Y", "Yttrium"),
    (40, r"Zr", "Zirconium"),
    (41, r"Nb", "Niobium"),
    (42, r"Mo", "Molybdenum"),
    (43, r"Tc", "Technetium"),
    (44, r"Ru", "Ruthenium"),
    (45, r"Rh", "Rhodium"),
    (46, r"Pd", "Palladium"),
    (47, r"Ag", "Silver"),
    (48, r"Cd", "Cadmium"),
    (49, r"In", "Indium"),
    (50, r"Sn", "Tin"),
    (51, r"Sb", "Antimony"),
    (52, r"Te", "Tellurium"),
    (53, r"I", "Iodine"),
    (54, r"Xe", "Xenon"),
    (55, r"Cs", "Caesium"),
    (56, r"Ba", "Barium"),
    (57, r"La", "Lanthanum"),
    (58, r"Ce", "Cerium"),
    (59, r"Pr", "Praseodymium"),
    (60, r"Nd", "Neodymium"),
    (61, r"Pm", "Promethium"),
    (62, r"Sm", "Samarium"),
    (63, r"Eu", "Europium"),
    (64, r"Gd", "Gadolinium"),
    (65, r"Tb", "Terbium"),
    (66, r"Dy", "Dysprosium"),
    (67, r"Ho", "Holmium"),
    (68, r"Er", "Erbium"),
    (69, r"Tm", "Thulium"),
    (70, r"Yb", "Ytterbium"),
    (71, r"Lu", "Lutetium"),
    (72, r"Hf", "Hafnium"),
    (73, r"Ta", "Tantalum"),
    (74, r"W", "Tungsten"),
    (75, r"Re", "Rhenium"),
    (76, r"Os", "Osmium"),
    (77, r"Ir", "Iridium"),
    (78, r"Pt", "Platinum"),
    (79, r"Au", "Gold"),
    (80, r"Hg", "Mercury"),
    (81, r"Tl", "Thallium"),
    (82, r"Pb", "Lead"),
    (83, r"Bi", "Bismuth"),
    (84, r"Po", "Polonium"),
    (85, r"At", "Astatine"),
    (86, r"Rn", "Radon"),
    (87, r"Fr", "Francium"),
    (88, r"Ra", "Radium"),
    (89, r"Ac", "Actinium"),
    (90, r"Th", "Thorium"),
    (91, r"Pa", "Protactinium"),
    (92, r"U", "Uranium"),
    (93, r"Np", "Neptunium"),
    (94, r"Pu", "Plutonium"),
    (95, r"Am", "Americium"),
    (96, r"Cm", "Curium"),
    (97, r"Bk", "Berkelium"),
    (98, r"Cf", "Californium"),
    (99, r"Es", "Einsteinium"),
    (100, r"Fm", "Fermium"),
    (101, r"Md", "Mendelevium"),
    (102, r"No", "Nobelium"),
    (103, r"Lr", "Lawrencium"),
    (104, r"Rf", "Rutherfordium"),
    (105, r"Db", "Dubnium"),
    (106, r"Sg", "Seaborgium"),
    (107, r"Bh", "Bohrium"),
    (108, r"Hs", "Hassium"),
    (109, r"Mt", "Meitnerium"),
    (110, r"Ds", "Darmstadtium"),
    (111, r"Rg", "Roentgenium"),
    (112, r"Cn", "Copernicium"),
    (113, r"Nh", "Nihonium"),
    (114, r"Fl", "Flerovium"),
    (115, r"Mc", "Moscovium"),
    (116, r"Lv", "Livermorium"),
    (117, r"Ts", "Tennessine"),
    (118, r"Og", "Oganesson"),
]


# We sort by symbol name length so He is captured before H
def sym(t): return len(t[1])

identifiers = {
    r"\alembic": "⚗",  # &#x2697;
    r"\atom": "⚛",  # &#x269b;
    r"\radioactive": "☢",  # &#x2622;
    r"\biohazard": "☣",  # &#x2623;
    r"\poisonold": "☠",  # &#x2620;
    r"\equilibrium": "⇌",  # &Equilibrium;
    r"\reverseequilibrium": "⇋",  # &ReverseEquilibrium;
    r"\biequation": "⇄",  # &rightleftarrows;
    r"\requation": "→",  # &rightarrow;
    r"\Requation": "⟶",  # &longrightarrow;
    r"\lequation": "←",  # &leftarrow;
    r"\Lequation": "⟵",  # &longleftarrow;
    r"\aqua": "q",  # q
    r"\liquid": "l",  # l
    r"\gas": "g",  # g
    r"\solid": "s",  # s
    r"\togas": "↑",  # &uparrow;
    r"\tosolid": "↓",  # &downarrow;
}

for atomic_number, symbol, name in sorted(_ELEMENTS, key=sym, reverse=True):
    identifiers[symbol] = identifiers[name] = (symbol, normal())
