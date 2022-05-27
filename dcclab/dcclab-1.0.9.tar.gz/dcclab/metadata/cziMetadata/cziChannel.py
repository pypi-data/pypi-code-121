class CZIChannel:
    def __init__(self, channelInformation, filters, root):
        self.channelId = '{};{}'.format(channelInformation[2], channelInformation[0])
        self.channel = channelInformation[0]
        self.channelName = channelInformation[1]
        self.filePath = channelInformation[2]
        self.root = root

        # These variables get their testData from filter objects.
        self.exWavelengthFilter = self.setExWavelengthFilter(filters)
        self.emWavelengthFilter = self.setEmWavelengthFilter(filters)
        self.beamSplitter = self.setBeamSplitter(filters)

        # These variables get their testData from root.
        self.reflector = self.setReflector()
        self.contrastMethod = self.setContrastMethod()
        self.lightSource = self.setLightSource()
        self.lightSourceIntensity = self.setLightSourceIntensity()
        self.dyeName = self.setDyeName()
        self.channelColor = self.setChannelColor()
        self.exWavelength = self.setExWavelength()
        self.emWavelength = self.setEmWavelength()
        self.effectiveNA = self.setEffectiveNA()
        self.imagingDevice = self.setImagingDevice()
        self.cameraAdapter = self.setCameraAdapter()
        self.exposureTime = self.setExposureTime()
        self.binningMode = self.setBinningMode()

    def __repr__(self):
        return '{};{};{};{}'.format(self.channel, self.channelName, self.exWavelengthFilter, self.emWavelengthFilter)

    def __eq__(self, other):
        return repr(self) == repr(other)

    def asDict(self):
        return {'file_path': self.filePath, 'channel_id': self.channelId, 'channel_name': self.channelName,
                'ex_wavelength_filter': self.exWavelengthFilter, 'em_wavelength_filter': self.emWavelengthFilter,
                'beam_splitter': self.beamSplitter, 'reflector': self.reflector, 'contrast_method': self.contrastMethod,
                'light_source': self.lightSource, 'light_source_intensity': self.lightSourceIntensity,
                'dye_name': self.dyeName, 'channel_color': self.channelColor, 'ex_wavelength': self.exWavelength,
                'em_wavelength': self.emWavelength, 'effective_na': self.effectiveNA,
                'imaging_device': self.imagingDevice, 'camera_adapter': self.cameraAdapter,
                'exposure_time': self.exposureTime, 'binning_mode': self.binningMode}

    @property
    def keys(self):
        return {'file_path': 'TEXT', 'channel_id': 'TEXT PRIMARY KEY', 'channel_name': 'TEXT', 'ex_wavelength_filter': 'TEXT',
                'em_wavelength_filter': 'TEXT', 'beam_splitter': 'INTEGER', 'reflector': 'TEXT',
                'contrast_method': 'TEXT', 'light_source': 'TEXT', 'light_source_intensity': 'REAL', 'dye_name': 'TEXT',
                'channel_color': 'TEXT', 'ex_wavelength': 'INTEGER', 'em_wavelength': 'INTEGER', 'effective_na': 'REAL',
                'imaging_device': 'TEXT', 'camera_adapter': 'TEXT', 'exposure_time': 'REAL', 'binning_mode': 'REAL'}

    def setExWavelengthFilter(self, filters):
        try:
            for filter in filters:
                if filter.getType() == 'Excitation' and self.channel == filter.getChannelId():
                    return filter.getFilterRange()
            return None
        except Exception:
            return None

    def setEmWavelengthFilter(self, filters):
        try:
            for filter in filters:
                if filter.getType() == 'Emission' and self.channel == filter.getChannelId():
                    return filter.getFilterRange()
            return None
        except Exception:
            return None

    def setBeamSplitter(self, filters):
        try:
            for filter in filters:
                if self.channel == filter.getChannelId():
                    return filter.getDichroic()
            return None
        except Exception:
            return None

    def setReflector(self):
        try:
            return self.root.find('./Metadata/Information/Image/Dimensions/Channels/Channel[@Id="{}"]'
                                  '/Reflector'.format(self.channel)).text
        except Exception:
            return None

    def setContrastMethod(self):
        try:
            return self.root.find('./Metadata/Information/Image/Dimensions/Channels/Channel[@Id="{}"]'
                                  '/ContrastMethod'.format(self.channel)).text
        except Exception:
            return None

    def setLightSource(self):
        try:
            lightId = self.root.find('./Metadata/Information/Image/Dimensions/Channels/Channel[@Id="{}"]'
                                     '/LightSourcesSettings/LightSourceSettings/LightSource'.format(self.channel)).attrib['Id']
            return self.root.find('./Metadata/Information/Instrument/LightSources'
                                  '/LightSource[@Id="{}"]'.format(lightId)).attrib['Name']
        except Exception:
            return None

    def setLightSourceIntensity(self):
        try:
            return float(self.root.find('./Metadata/Information/Image/Dimensions/Channels/Channel[@Id="{}"]'
                                        '/LightSourcesSettings/LightSourceSettings/Intensity'.format(self.channel)).text.rstrip('%'))
        except Exception:
            return None

    def setDyeName(self):
        try:
            return self.root.find('./Metadata/DisplaySetting/Channels/Channel[@Id="{}"]'
                                  '/DyeName'.format(self.channel)).text
        except Exception:
            return None

    def setChannelColor(self):
        try:
            return self.root.find('./Metadata/Information/Image/Dimensions/Channels/Channel[@Id="{}"]'
                                  '/Color'.format(self.channel)).text
        except Exception:
            return None

    def setExWavelength(self):
        try:
            return int(self.root.find('./Metadata/Information/Image/Dimensions/Channels/Channel[@Id="{}"]'
                                      '/ExcitationWavelength'.format(self.channel)).text)
        except Exception:
            return None

    def setEmWavelength(self):
        try:
            return int(self.root.find('./Metadata/Information/Image/Dimensions/Channels/Channel[@Id="{}"]'
                                      '/EmissionWavelength'.format(self.channel)).text)
        except Exception:
            return None

    def setExposureTime(self):
        try:
            return float(self.root.find('./Metadata/Information/Image/Dimensions/Channels/'
                                        'Channel[@Id="{}"]/ExposureTime'.format(self.channel)).text) / 1E6
        except Exception:
            return None

    def setEffectiveNA(self):
        try:
            return float(self.root.find('./Metadata/Information/Instrument/Objectives/Objective/LensNA').text)
        except Exception:
            return None

    def setImagingDevice(self):
        try:
            return self.root.find('./Metadata/Information/Instrument/Detectors/Detector').attrib['Name']
        except Exception:
            return None

    def setCameraAdapter(self):
        try:
            return self.root.find('./Metadata/Information/Instrument/Detectors/Detector/Adapter/Manufacturer/Model').text
        except Exception:
            return None

    def setBinningMode(self):
        try:
            return float(self.root.find('./Metadata/Information/Image/Dimensions/Channels/Channel/'
                                        'DetectorSettings/Binning').text.replace(',', '.'))
        except Exception:
            return None
