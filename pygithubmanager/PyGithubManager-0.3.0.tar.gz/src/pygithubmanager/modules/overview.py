from datetime import date

import requests
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout
from dateutil.relativedelta import relativedelta
from github.PaginatedList import PaginatedList

from ui.widgets import Ui_Overview
from widgets import MplCanvas
from widgets.PopularRepository import PopularRepository


class Overview(QWidget):
    def __init__(self, user):
        """
        Widgets for the overview tab to show the user's information

        Parameters
        ----------
        user : User
            User object to show the information
        """
        super(Overview, self).__init__()
        self.ui = Ui_Overview()
        self.ui.setupUi(self)

        self.user = user

        self.load_popular_repos()
        self.load_contributions()

    @Slot()
    def load_popular_repos(self):
        """
        Loads the user's most popular repositories
        """
        popular_repos: PaginatedList = self.user.get_data().get_repos(visibility="public", sort="updated",
                                                                      direction="desc")
        positions = [(i, j) for i in range(2) for j in range(2)]
        for positions, popular_repo in zip(positions, popular_repos):
            self.ui.gridLayout.addWidget(PopularRepository(popular_repo, self.user), *positions)

    @Slot()
    def load_contributions(self):
        """
        Loads the user's contributions
        """
        year = date.today().year
        response = requests.get(f'https://skyline.github.com/{self.user.user.login}/{year}.json',
                                auth=(self.user.get_data().login, self.user.token))
        weeks = []
        total = []
        if response.status_code == 200:
            for x in response.json()['contributions']:
                weeks.append((date(year, 1, 1) + relativedelta(weeks=+x['week'])).strftime('%d/%m'))
                acum = 0
                for y in x['days']:
                    acum += int(y['count'])
                total.append(acum)
            canvas = MplCanvas(width=10, height=10, dpi=65, xlabel='WEEKS', ylabel='TOTAL CONTRIBUTIONS',
                               title=f'{year} CONTRIBUTIONS', rotate_xlabel=True)
            canvas.ax.bar(weeks, total)
            self.ui.contributionsWidget.setLayout(QVBoxLayout(self.ui.contributionsWidget).addWidget(canvas))
