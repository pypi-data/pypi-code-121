from django.shortcuts import redirect
from otree.views import Page


class ProlificRedirect(Page):
    """Redirect back to Prolific"""

    def is_displayed(self):
        return not self.participant._is_bot

    def get(self):
        if "prolific_completion_code" in self.participant.vars:
            code = self.participant.vars["prolific_completion_code"]
        elif "prolific_completion_code" in self.session.config:
            code = self.session.config["prolific_completion_code"]
        else:
            raise LookupError(
                "Could not find 'prolific_completion_code' in participant.vars or session.config"
            )

        self._record_page_completion_time()
        # do not increment the number of pages, this way when a participant uses the link again they will still be redirected to Prolific
        # self._increment_index_in_pages()

        return redirect(f"https://app.prolific.co/submissions/complete?cc={code}")
