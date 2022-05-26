    """_summary_

    Returns:
        _type_: _description_
    """

class Area:
    """ Data infrastructure for NOC wage and outlook """
    data = [
        ["Canada", "Canada", 0],
        ["Newfoundland and Labrador", "Newfoundland and Labrador", 1],
        ["Newfoundland and Labrador", "Avalon Peninsula Region", 2],
        ["Newfoundland and Labrador", "Notre Dame-Central-Bonavista Bay Region", 3],
        ["Newfoundland and Labrador", "South Coast–Burin Peninsula Region", 4],
        ["Newfoundland and Labrador", "West Coast–Northern Peninsula–Labrador Region", 5],
        ["Prince Edward Island", "Prince Edward Island", 6],
        ["Nova Scotia", "Nova Scotia", 7],
        ["Nova Scotia", "Annapolis Valley Region", 8],
        ["Nova Scotia", "Cape Breton Region", 9],
        ["Nova Scotia", "Halifax Region", 10],
        ["Nova Scotia", "North Shore Region", 11],
        ["Nova Scotia", "Southern Region", 12],
        ["New Brunswick", "New Brunswick", 13],
        ["New Brunswick", "Campbellton–Miramichi Region", 14],
        ["New Brunswick", "Edmundston–Woodstock Region", 15],
        ["New Brunswick", "Fredericton–Oromocto", 16],
        ["New Brunswick", "Moncton–Richibucto Region", 17],
        ["New Brunswick", "Saint John–St. Stephen Region", 18],
        ["Quebec", "Quebec", 19],
        ["Quebec", "Abitibi-Témiscamingue Region", 20],
        ["Quebec", "Bas-Saint-Laurent Region", 21],
        ["Quebec", "Capitale-Nationale Region", 22],
        ["Quebec", "Centre-du-Québec Region", 23],
        ["Quebec", "Chaudière-Appalaches Region", 24],
        ["Quebec", "Côte-Nord Region", 25],
        ["Quebec", "Estrie Region", 26],
        ["Quebec", "Gaspésie–Îles-de-la-Madeleine Region", 27],
        ["Quebec", "Lanaudière Region", 28],
        ["Quebec", "Laurentides Region", 29],
        ["Quebec", "Laval Region", 30],
        ["Quebec", "Mauricie Region", 31],
        ["Quebec", "Montréal Region", 32],
        ["Quebec", "Montérégie Region", 33],
        ["Quebec", "Nord-du-Québec Region", 34],
        ["Quebec", "Outaouais Region", 35],
        ["Quebec", "Saguenay–Lac-Saint-Jean Region", 36],
        ["Ontario", "Ontario", 37],
        ["Ontario", "Hamilton–Niagara Peninsula Region", 38],
        ["Ontario", "Kingston–Pembroke Region", 39],
        ["Ontario", "Kitchener–Waterloo–Barrie Region", 40],
        ["Ontario", "London Region", 41],
        ["Ontario", "Muskoka–Kawarthas Region", 42],
        ["Ontario", "Northeast Region", 43],
        ["Ontario", "Northwest Region", 44],
        ["Ontario", "Ottawa Region", 45],
        ["Ontario", "Stratford–Bruce Peninsula Region", 46],
        ["Ontario", "Toronto Region", 47],
        ["Ontario", "Windsor-Sarnia Region", 48],
        ["Manitoba", "Manitoba", 49],
        ["Manitoba", "Interlake Region", 50],
        ["Manitoba", "North Central Region", 51],
        ["Manitoba", "North Region", 52],
        ["Manitoba", "Parklands Region", 53],
        ["Manitoba", "South Central Region", 54],
        ["Manitoba", "Southeast Region", 55],
        ["Manitoba", "Southwest Region", 56],
        ["Manitoba", "Winnipeg Region", 57],
        ["Saskatchewan", "Saskatchewan", 58],
        ["Saskatchewan", "Northern Region", 59],
        ["Saskatchewan", "Prince Albert Region", 60],
        ["Saskatchewan", "Regina–Moose Mountain Region", 61],
        ["Saskatchewan", "Saskatoon–Biggar Region", 62],
        ["Saskatchewan", "Swift Current–Moose Jaw Region", 63],
        ["Saskatchewan", "Yorkton–Melville Region", 64],
        ["Alberta", "Alberta", 65],
        ["Alberta", "Athabasca–Grande Prairie–Peace River Region", 66],
        ["Alberta", "Banff–Jasper–Rocky Mountain House Region", 67],
        ["Alberta", "Calgary Region", 68],
        ["Alberta", "Camrose–Drumheller Region", 69],
        ["Alberta", "Edmonton Region", 70],
        ["Alberta", "Lethbridge–Medicine Hat Region", 71],
        ["Alberta", "Red Deer Region", 72],
        ["Alberta", "Wood Buffalo–Cold Lake Region", 73],
        ["British Columbia", "British Columbia", 74],
        ["British Columbia", "Cariboo Region", 75],
        ["British Columbia", "Kootenay Region", 76],
        ["British Columbia", "Lower Mainland–Southwest Region", 77],
        ["British Columbia", "Nechako Region", 78],
        ["British Columbia", "North Coast Region", 79],
        ["British Columbia", "Northeast Region", 80],
        ["British Columbia", "Thompson–Okanagan Region", 81],
        ["British Columbia", "Vancouver Island and Coast Region", 82],
        ["Yukon Territory", "Yukon Territory", 83],
        ["Northwest Territories", "Northwest Territories", 84],
        ["Nunavut", "Nunavut", 85]
        ]
    
    #col 1 is index for prince in wage/outlook search, col 2,3 is area range, 4 is index of province for provincial median wage search
    prov_area=[     
        [1,2,5,4],    # Newfoundland and Labrador
        [6,6,6,9],    # Prince Edward Island
        [7,8,12,6],   # Nova Scotia
        [13,14,18,3], # New Brunswick
        [19,20,36,10], # Quebec
        [37,38,48,8], # Ontario
        [49,50,57,2], # Manitoba
        [58,59,64,11], # Saskatchewan
        [65,66,73,0], # Alberta
        [74,75,82,1], # British Columbia
        [83,83,83,12], # Yukon Territory
        [84,84,84,5], # Northwest Territories
        [85,85,85,7]  # Nunavut
    ]

    def __init__(self,areaId=77):
        self.areaId=areaId

    def index(self,area_name):
        index=0
        for area in Area.data:
            if area_name==area[1]:
                return index
            index+=1

    # for wage/outlook
    @property
    def prov_index(self):  
        for pa in Area.prov_area:
            if (self.areaId>=pa[1]) & (self.areaId<=pa[2]):
                return pa[0] 

    # for provincial median wage https://www.canada.ca/en/employment-social-development/services/foreign-workers/service-tables.html
    @property
    def prov_index_median_wage(self):  
        for pa in Area.prov_area:
            if (int(self.areaId)>=pa[1]) & (int(self.areaId)<=pa[2]):
                return pa[3] 
    @property
    def prov_name(self):
        for ai in Area.data:
            if ai[2]==int(self.areaId):
                return ai[0]
    @property
    def area_name(self):
        for ai in Area.data:
            if ai[2]==int(self.areaId):
                return ai[1]