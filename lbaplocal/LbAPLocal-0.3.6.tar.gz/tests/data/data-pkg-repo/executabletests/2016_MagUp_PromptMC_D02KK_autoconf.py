from Configurables import DaVinci
try:
    DaVinci().Turbo = False
except AttributeError:
    # Older DaVinci versions don't support Turbo at all
    pass

DaVinci().InputType = 'DST'
DaVinci().DataType = '2016'
DaVinci().Simulation = True
DaVinci().Lumi = False
DaVinci().DDDBtag = 'dddb-20170721-3'
DaVinci().CondDBtag = 'sim-20170721-2-vc-mu100'