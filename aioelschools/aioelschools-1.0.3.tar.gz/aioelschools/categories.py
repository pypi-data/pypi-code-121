from .methods import login, user, dictionary, department, chart


class ElschoolCategories:
    @property
    def login(self) -> login.LoginCategory:
        return login.LoginCategory()

    @property
    def user(self) -> user.UserCategory:
        return user.UserCategory()

    @property
    def dictionary(self) -> dictionary.DictionaryCategory:
        return dictionary.DictionaryCategory()

    @property
    def department(self) -> department.DepartmentCategory:
        return department.DepartmentCategory()

    @property
    def chart(self) -> chart.ChartCategory:
        return chart.ChartCategory()