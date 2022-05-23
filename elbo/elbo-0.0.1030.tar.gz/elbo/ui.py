import json
import logging

import coloredlogs
import questionary
from inquirer.themes import GreenPassion, term

logger = logging.getLogger("elbo.client")
coloredlogs.install(level="DEBUG", logger=logger, fmt="%(name)s %(message)s")


class ElboTheme(GreenPassion):
    def __init__(self):
        super().__init__()
        self.Question.mark_color = term.yellow
        self.Question.brackets_color = term.pink
        self.Question.default_color = term.yellow
        self.Checkbox.selection_color = term.bold_black_on_pink
        self.Checkbox.selection_icon = "❯"
        self.Checkbox.selected_icon = "◉"
        self.Checkbox.selected_color = term.pink
        self.Checkbox.unselected_color = term.normal
        self.Checkbox.unselected_icon = "◯"
        self.List.selection_color = term.bold_black_on_pink
        self.List.selection_cursor = "❯"
        self.List.unselected_color = term.normal


def prompt_user(compute_options):
    """
    Prompt the user with compute options and get the selection
    :param compute_options: The list of compute options
    :return: The selected option
    """
    options = []
    mapping = {}

    def get_sorting_key(x):
        x_parsed = json.loads(x[1])
        return x_parsed["cost"]

    compute_options = dict(
        sorted(compute_options.items(), key=lambda x: get_sorting_key(x))
    )
    for k, v in compute_options.items():
        v = json.loads(v)
        if v.get("spot") is True:
            suffix = "(spot)"
        else:
            suffix = ""
        k = k.replace(" (spot)", "")
        provider = v["provider"]

        if "linode" in provider.lower():
            provider = f"{provider} (~ 9 mins to provision) (billed hourly)"
        option = (
            f" ${v['cost']:7.4f}/hour {k:>26} {v['num_cpu']:>3} cpu {v['mem']:>5}Gb mem "
            f"{v['gpu_mem']:>4}Gb gpu-mem {provider} {suffix}"
        )
        options.append(option)
        mapping[option] = v

    if len(options) > 1:
        logger.info(f"number of compute choices - {len(options)}")
        chosen = questionary.select(
            "Please choose:",
            choices=options,
        ).ask()
        if chosen is None:
            logger.warning(f"None selected, exiting.")
            exit(0)
            return None
        chosen_compute_type = mapping[chosen]
    elif len(options) == 0:
        logger.error(
            f"was unable to find compute options at the moment. Please email support@elbo.ai if this continues."
        )
        return None
    else:
        chosen_compute_type = list(mapping.values())[0]

    return chosen_compute_type
