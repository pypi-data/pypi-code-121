from django.forms import widgets
import numbers
import math

permitted_info_block = ["left", "right"]
non_permitted_block_msg = "Choose between two options: {}".format(
    " or ".join(permitted_info_block)
)
no_range_set_err_msg = "Both max and min parameters should be set to use this slider"


class AdvancedSliderWidget(widgets.NumberInput):
    class Media:
        css = {
            "all": (
                "https://code.jquery.com/ui/1.10.3/themes/smoothness/jquery-ui.css",
                "jquery-ui/jquery.ui.labeledslider.css",
                "css/slider.css",
            )
        }
        js = (
            "https://code.jquery.com/ui/1.10.3/jquery-ui.js",
            "jquery-ui/jquery.ui.labeledslider.js",
        )

    template_name = "otree_survey/widgets/tickslider.html"
    # TODO: provide a chance for user not to give min and max
    # default_min = 0
    # default_max = 10
    # default_range = 10
    default_nsteps = 10
    default_med_value = 5
    ndigits = 0
    suffix = ""

    def __init__(
        self,
        show_ticks=True,
        show_value=True,
        show_block="left",
        ndigits=None,
        end_labels=None,
        set_default=False,
        *args,
        **kwargs
    ):
        self.show_ticks = show_ticks
        self.show_value = show_value
        self.ndigits = ndigits
        assert show_block in permitted_info_block, non_permitted_block_msg
        self.show_block = show_block
        assert end_labels is None or len(end_labels) == 2
        self.end_labels = end_labels
        self.set_default = set_default
        super().__init__(*args, **kwargs)

    def set_steps(self, smin, smax):
        slider_range = smax - smin
        step = round(slider_range / self.default_nsteps, 2)
        return step

    def set_digits(self, step):
        if self.ndigits is None:
            if isinstance(step, int):
                self.ndigits = 0
                return
            frac, _ = math.modf(step)
            strfrac = str(frac).split(".")[1]
            self.ndigits = len(strfrac)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        a_ = context["widget"]["attrs"]
        assert all(i in a_ for i in ["min", "max"]), no_range_set_err_msg
        # TODO: allow user to skip max/min providing default options (partly based on step/tick_interval options)
        # wi_attrs.setdefault('min', self.default_min)
        # wi_attrs.setdefault('max', self.default_max)
        if not isinstance(a_.get("step"), numbers.Number):
            a_["step"] = self.set_steps(a_["min"], a_["max"])
        self.set_digits(a_["step"])
        a_["ndigits"] = self.ndigits

        a_.setdefault("tick_interval", a_["step"])
        a_.setdefault("secondary_ticks", self.show_ticks)
        a_.setdefault("show_ticks", True)
        self.default_med_value = round((a_["min"] + a_["max"]) / 2, self.ndigits)
        if self.ndigits == 0:
            self.default_med_value = int(self.default_med_value)
        a_["set_value"] = True
        if value == "":
            value = None
        a_["slider_start_value"] = value
        if value is None:
            a_["set_value"] = False
            if type(self.set_default) == int:
                a_["slider_start_value"] = self.set_default
            elif self.set_default is True:
                a_["slider_start_value"] = self.default_med_value
        a_.setdefault("suffix", self.suffix)
        a_["show_value"] = self.show_value
        a_["show_block"] = self.show_block
        a_["end_labels"] = self.end_labels
        return context
