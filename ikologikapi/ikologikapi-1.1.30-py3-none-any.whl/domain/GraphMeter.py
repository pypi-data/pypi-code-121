class GraphMeter:
    def __init__(self):
        self.id = None
        self.customer = None
        self.installation = None

        self.type = None
        self.name = None
        self.identification = None
        self.description = None
        self.importStatus = None
        self.unit = None
        self.valueType = None
        self.valueTimeUnit = None
        self.decimalPrecision = None
        self.color = None

        self.visible = None
        self.visibleTroubleshooting = None

        self.gridAlignmentValue = None
        self.gridAlignmentUnit = None

        self.transformationActive = None
        self.transformationMultiplier = None
        self.transformationAdd = None
        self.transformationRounding = None

        self.minLimit = None
        self.lowLowLimit = None
        self.lowLimit = None
        self.highLimit = None
        self.highHighLimit = None
        self.maxLimit = None

        self.medianActive = None
        self.medianSampleSize = None

        self.trendActive = None
        self.trendSampleSize = None

        self.epsilon = None

        self.dataImportStatus = None
        self.lastDataImportStatusUpdate = None

        self.firstData = None
        self.firstDate = None
        self.firstValue = None
        self.firstDuration = None

        self.lastData = None
        self.lastDate = None
        self.lastValue = None
        self.lastDuration = None

        self.minData = None
        self.minDate = None
        self.minValue = None
        self.minDuration = None

        self.maxData = None
        self.maxDate = None
        self.maxValue = None
        self.maxDuration = None

        self.dataCount = None
        self.valueCount = None
        self.average = None

        self.alertsIActive = None
        self.alertsIActiveMessages = None
        self.alertsWActive = None
        self.alertsWActiveMessages = None
        self.alertsAActive = None
        self.alertsAActiveMessages = None
        self.alertsLLActive = None
        self.alertsLLActiveMessages = None
        self.alertsLActive = None
        self.alertsLActiveMessages = None
        self.alertsHActive = None
        self.alertsHActiveMessages = None
        self.alertsHHActive = None
        self.alertsHHActiveMessages = None

        self.userMeterSettings = None
