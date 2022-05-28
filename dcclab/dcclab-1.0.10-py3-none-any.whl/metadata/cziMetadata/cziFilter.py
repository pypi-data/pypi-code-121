class CZIFilter:
    def __init__(self, filterId, root):
        self.filterId = filterId
        self.root = root

        self.filterSetId, self.filterType = self.setFilterSetIdAndFilterType()
        self.channelId = self.setChannelId()
        self.cutIn = self.setCutIn()
        self.cutOut = self.setCutOut()
        self.dichroicId = self.setDichroicId()
        self.dichroic = self.setDichroic()

    def __repr__(self):
        return '{};{};{};{}-{}'.format(self.filterId, self.channelId, self.filterType, self.cutIn, self.cutOut)

    def __eq__(self, other):
        return repr(self) == repr(other)

    def setFilterSetIdAndFilterType(self):
        try:
            for filterSet in self.root.find('./Metadata/Information/Instrument/FilterSets'):
                if self.filterId == filterSet.find('./EmissionFilters/EmissionFilterRef').attrib['Id']:
                    return filterSet.attrib['Id'], 'Emission'
                if self.filterId == filterSet.find('./ExcitationFilters/ExcitationFilterRef').attrib['Id']:
                    return filterSet.attrib['Id'], 'Excitation'
            return None, None
        except Exception:
            return None, None

    def setChannelId(self):
        try:
            for channel in self.root.find('./Metadata/Information/Image/Dimensions/Channels'):
                if channel.find('FilterSetRef').attrib['Id'] == self.filterSetId:
                    return channel.attrib['Id']
        except Exception:
            return None

    def setCutIn(self):
        try:
            return int(self.root.find('./Metadata/Information/Instrument/Filters/Filter[@Id="{}"]'
                                      '/TransmittanceRange/CutIn'.format(self.filterId)).text)
        except Exception:
            return None

    def setCutOut(self):
        try:
            return int(self.root.find('./Metadata/Information/Instrument/Filters/Filter[@Id="{}"]'
                                      '/TransmittanceRange/CutOut'.format(self.filterId)).text)
        except Exception:
            return None

    def setDichroicId(self):
        try:
            return self.root.find('./Metadata/Information/Instrument/FilterSets/'
                                  'FilterSet[@Id="{}"]/DichroicRef'.format(self.filterSetId)).attrib['Id']
        except Exception:
            return None

    def setDichroic(self):
        try:
            return int(self.root.find('./Metadata/Information/Instrument/Dichroics/'
                                      'Dichroic[@Id="{}"]/Wavelengths/Wavelength'.format(self.dichroicId)).text)
        except Exception:
            return None

    def getType(self):
        return self.filterType

    def getChannelId(self):
        return self.channelId

    def getFilterRange(self):
        return '{}-{}'.format(self.cutIn, self.cutOut)

    def getDichroic(self):
        return self.dichroic