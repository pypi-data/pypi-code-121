from edc_model_wrapper.wrappers import ModelWrapper


class SubjectLocatorModelWrapper(ModelWrapper):

    model = "edc_locator.subjectlocator"
    next_url_name = "subject_dashboard_url"
    next_url_attrs = ["subject_identifier"]
