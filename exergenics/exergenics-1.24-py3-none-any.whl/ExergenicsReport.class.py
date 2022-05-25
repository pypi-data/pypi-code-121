'''
*****************************
ExergenicsReport.class.py
*****************************

J.CHRISTIAN FEB 2022
Prepare and Submit an Exergenics Report to be sent to portal
'''



class ExergenicsReport:

    buildingCode, plantCode = None, None

    recommendation_chillerStaging = "chillerStaging"
    recommendation_dynamicCondenser = "dynamicCondenser"
    recommendation_loadBalancing = "loadBalancing"
    recommendation_CWPSM = "CWPSM"

    report = {}

    sections = {
        "PLANT_SCORE": {
            "required": True,
        },
        "CONTROLS_RECOMMENDATIONS": {
            "required": True,
        },
        "FINANCIAL_RESULTS": {
            "required": True,
        },
        "COST_PAYBACK": {
            "required": True,
        },
        "AVERAGE_CHILLED_WP_COP": {
            "required": True,
        },
        "ENVIRONMENTAL_RESULTS": {
            "required": True,
        },
        "SETPOINTS_STAGE_UP": {
            "required": True,
        },
        "SETPOINTS_STAGE_DOWN": {
            "required": True,
        },
        "CHILLER_STRATEGY": {
            "required": True,
        },
        "TEMPERATURE_ALGORITHM": {
            "required": True,
        },
        "CHART_DYNAMIC_TEMP_ALGORITHM": {
            "required": True,
        },
        "LOAD_BALANCE_CHILLER_TEXT": {
            "required": True,
        },
        "CHART_CHILLER_STAGING_STRATEGY": {
            "required": True,
        },
        "LOAD_BALANCE_STAGE": {
            "required": True,
            "incremental": True,
            "incrementStart": 1
        },
        "LOAD_BALANCE_STAGE_LIMITS": {
            "required": True,
            "incremental": True,
            "incrementStart": 1,
            "currentIncrement": 1
        },
        "PERFORMANCE_METRICS": {
            "required": True
        },
    }

    def __init__(self, buildingCode, plantCode):
        self.buildingCode = buildingCode
        self.plantCode = plantCode

    def setPlantScore(self, ps):
        self.report["PLANT_SCORE"] = ps

    def setSimulatedSavingsPotential(self, recommendationTag, savingsKwh, savingsPeak):
        self.report["CONTROLS_RECOMMENDATIONS"][recommendationTag] = (savingsKwh, savingsPeak)

    def set

r = ExergenicsReport("TEST", "TEST-PLANT-1")

''' Overall Plant Score '''
r.setPlantScore(92)

''' Control Strategy Recommendations - Simulated Savings Potential (%) '''
r.setSimulatedSavingsPotential(r.recommendation_chillerStaging, 0.03, 0.02)
r.setSimulatedSavingsPotential(r.recommendation_dynamicCondenser, 0.04, 0.04)
r.setSimulatedSavingsPotential(r.recommendation_loadBalancing, 0.05, 0.04)
r.setSimulatedSavingsPotential(r.recommendation_CWPSM, 0.06, 0.05)


