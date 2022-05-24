import importlib
import inspect
import random
import string
from typing import Type, List, Dict

import django.db.models as django_models
from otree.api import Page, BasePlayer, Submission


def gen_random_data(
    field_name, player_class, player, field_values: Dict[str, object] = None
):
    field: django_models.Field = player_class._meta.get_field(field_name)
    # default value
    if field_values and (field_name := str(field.attname)) in field_values:
        return field_values[field_name]
    # if blank allowed, leave blank with chance of 50%
    if field.blank:
        if random.randint(0, 1) == 0:
            return None
    try:
        # dynamic choices
        choices = getattr(player, f"{field_name}_choices")()
    except AttributeError:
        # static choices
        choices = field.choices
    # if choices, pick a random one
    if choices:
        choice = random.choice(choices)
        # return the first element of choice if field.choices follows the standard format:
        # [(A, B), (A, B) ...] where A is the actual value to be set on the model, and B is the human-readable name
        # (see https://docs.djangoproject.com/en/3.1/ref/models/fields/#choices)
        if type(choice) in (tuple, list) and len(choice) == 2:
            return choice[0]
        # otherwise return choice, although this is likely to break things
        return choice
    # if number, pick a random number between bounds
    # (use django fields which are the base class for oTree fields)
    # TODO change to get_min?
    print(isinstance(field, django_models.FloatField))
    if isinstance(field, django_models.IntegerField) or isinstance(
        field, django_models.FloatField
    ):
        min = getattr(field, "min", 0)
        max = getattr(field, "max", 10)
        return random.randint(min, max)
    # elif string, generate random string, respecting minimum length
    # TODO add min length
    elif isinstance(field, django_models.TextField):
        chars = string.ascii_letters + string.punctuation
        return "".join(random.choice(chars) for _ in range(20))
    # TODO else raise error
    raise NotImplementedError(f"Cannot generate data for {field_name}")


class AutoBot:
    """AutoBot fills in oTree fields automatically.

    Abstract Mixin.  Usage:
    ```
    PlayerBot(AutoBot, Bot)
    ```
    where `Bot` comes from the module __init__.py.

    For each round uses the `page_sequence` from the apps page module,
    unless you specify a `custom_page_sequence` attribute, with one page sequence per round.

    To manually specify data used in testing, including to overcome the blow limitations,
    use the `custom_field_values` attribute, with one set of values per entry.

    TODO Page form fields

    TODO Limitations:
    - only some fields
    - min/max
    - custom clean method
    - bad choices
    - player fields only
    """

    custom_page_sequence: Dict[int, List[Page]]
    custom_field_values: List[Dict[str, object]]

    def play_round(self):
        assert hasattr(self, "PlayerClass"), (
            "AutoBot needs to be used as a mixin, " "e.g. class PlayerBot(Bot, AutoBot)"
        )

        # module of app in which the Autobot is used (subclassed)
        player_class: Type[BasePlayer] = self.PlayerClass
        models_module = inspect.getmodule(player_class)

        field_values = (
            random.choice(self.custom_field_values)
            if hasattr(self, "custom_field_values")
            else None
        )

        # page_sequence of the app
        page_sequence: List[Page]
        if hasattr(self, "custom_page_sequence"):
            page_sequence = self.custom_page_sequence[self.round_number]
        else:
            # all pages
            pages_module = importlib.import_module(f"{models_module.__package__}.pages")
            page_sequence = pages_module.page_sequence

        for page in page_sequence:
            page_inst = page()
            try:
                # see FormPageOrInGameWaitPage.dispatch()
                page_inst.set_attributes(participant=self.player.participant)
            except KeyError:
                # error in otree.lookup.get_page_lookup
                # bot should not be on this page
                continue

            if not page_inst.is_displayed():
                continue

            random_data, fields = {}, None
            fields = page_inst.get_form_fields()
            if fields:
                assert page.form_model == "player"
                random_data = {
                    field: gen_random_data(
                        field,
                        player_class,
                        self.player,
                        field_values,
                    )
                    for field in fields
                }
                # remove empty fields (oTree does not allow None, even if blank==True)
                random_data = {k: v for k, v in random_data.items() if v is not None}

            yield Submission(page, random_data)
