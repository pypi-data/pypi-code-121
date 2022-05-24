from __future__ import annotations

from dataclasses import dataclass
from typing import Union, List

import otree
from django.conf import settings
from django.utils import translation
from otree.views import abstract, Page


@dataclass
class ProgressItem:
    title: str
    width: int
    css_class: str = "col"


class SurveyPage(Page):
    show_progress = True

    def get_context_data(self, **context):
        context["show_back"] = self.allow_back()
        context["progress"] = self._progress()
        response = abstract.FormPageOrInGameWaitPage.get_context_data(self, **context)
        return response

    def get(self):
        # activate user-specific language
        translation.activate(self.participant.vars.get("lang", settings.LANGUAGE_CODE))

        # record visited pages, for use by progress bar
        if "_survey_pages_visited" not in self.participant.vars:
            self.participant.vars["_survey_pages_visited"] = set()
        self.participant.vars["_survey_pages_visited"].add(self._index_in_pages)

        return super(SurveyPage, self).get()

    def post(self):
        # evaluate form and save object
        response = super(SurveyPage, self).post()
        # go back if necessary
        if "back" in self.request.POST:
            self._go_back()
            return self._redirect_to_page_the_user_should_be_on()
        return response

    def _get_page(self, page_index: int) -> abstract.FormPageOrInGameWaitPage:
        url = otree.lookup.url_i_should_be_on(
            self.participant.code, self.participant._session_code, page_index
        )
        return abstract.get_view_from_url(url)()

    def _go_to_page(self, page_index: int) -> abstract.FormPageOrInGameWaitPage:
        # sanity checks
        assert (
            1 <= page_index <= self.participant._max_page_index
        ), "page_index out of range"
        page = self._get_page(page_index)
        # assert type(page) == abstract.WaitPage, 'cannot go back to a wait page'
        # TODO assert players_in_group == None

        # take participant to page_index
        self.participant._index_in_pages = page_index
        return page

    def _go_back(self):
        assert self._index_in_pages > 1, "participant is on first page, cannot go back"
        try:
            # loop over pages backwards, break if displayed
            # similar to self._increment_index_in_pages()
            for page_index in range(self._index_in_pages - 1, 0, -1):
                page = self._go_to_page(page_index)
                page.set_attributes(self.participant)
                if page.is_displayed():
                    break
            self._go_to_page(page_index)
        except:
            # reset the page index if something went wrong
            self.participant._index_in_pages = self._index_in_pages
            raise

    def allow_back(self) -> bool:
        return self.participant._index_in_pages > 1

    def _progress(self) -> Union[List[ProgressItem], None]:
        """If `show_progress` attribute is True, use the user-set `progress()` progress bars
        or (if unavailable) show the progress in terms of oTree page numbers (incl. hidden pages)"""

        if not self.show_progress:
            return None

        user_progress = self.progress()
        if user_progress:
            if type(user_progress) == int:
                user_progress = [ProgressItem("", user_progress)]
            return user_progress

        if "_survey_pages_total" in self.participant.vars:
            pages_until_here = [
                p
                for p in self.participant.vars["_survey_pages_visited"]
                if p <= self._index_in_pages
            ]
            progress = min(
                int(
                    (
                        len(pages_until_here)
                        / self.participant.vars["_survey_pages_total"]
                    )
                    * 100
                ),
                100,
            )
        else:
            progress = int(
                100
                * (self.participant._index_in_pages / self.participant._max_page_index)
            )

        return [ProgressItem("", progress)]

    def progress(self) -> Union[List[ProgressItem], int, None]:
        return None

    # list of fields we do not want to iterate over
    PLAYER_INTERNAL_FIELDS = [
        "id",
        "id_in_group",
        "_payoff",
        "participant",
        "session",
        "round_number",
        "subsession",
        "group",
    ]

    @property
    def all_player_fields(self):
        """All but internal fields, in order of declaration"""
        return [
            f.name
            for f in self.player._meta.fields
            if f.name not in self.PLAYER_INTERNAL_FIELDS
        ]
