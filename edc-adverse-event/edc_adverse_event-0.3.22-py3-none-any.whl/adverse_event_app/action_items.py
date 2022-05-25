from edc_action_item import site_action_items
from edc_action_item.action_with_notification import ActionWithNotification
from edc_constants.constants import HIGH_PRIORITY

from edc_adverse_event.action_items import (
    AeFollowupAction,
    AeInitialAction,
    AeSusarAction,
    AeTmgAction,
    DeathReportAction,
    DeathReportTmgAction,
    DeathReportTmgSecondAction,
)
from edc_adverse_event.constants import (
    AE_FOLLOWUP_ACTION,
    DEATH_REPORT_ACTION,
    STUDY_TERMINATION_CONCLUSION_ACTION,
)


class StudyTerminationConclusionAction(ActionWithNotification):
    name = STUDY_TERMINATION_CONCLUSION_ACTION
    display_name = "Submit Study Termination/Conclusion Report"
    notification_display_name = "Study Termination/Conclusion Report"
    parent_action_names = [
        DEATH_REPORT_ACTION,
        AE_FOLLOWUP_ACTION,
    ]
    reference_model = "adverse_event_app.studyterminationconclusion"
    show_link_to_changelist = True
    admin_site_name = "adverse_event_app_admin"
    priority = HIGH_PRIORITY


site_action_items.register(AeFollowupAction)
site_action_items.register(AeInitialAction)
site_action_items.register(AeSusarAction)
site_action_items.register(AeTmgAction)
site_action_items.register(DeathReportAction)
site_action_items.register(DeathReportTmgAction)
site_action_items.register(DeathReportTmgSecondAction)
site_action_items.register(StudyTerminationConclusionAction)
