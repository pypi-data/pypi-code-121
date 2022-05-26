from service.i18n import locales, static_translates


def test_locales():
    """Check read populated i18n locales."""
    populated = {'ru', 'en'}
    for locale in populated:
        assert locale in locales


def test_static_locales():
    """Check static locales."""
    en_translates = static_translates['en']
    assert en_translates.gettext('Error') == 'Error'
    assert en_translates.gettext('Success') == 'Success'

    ru_translates = static_translates['ru']
    assert ru_translates.gettext('Error') == 'Ошибка'
    assert ru_translates.gettext('Success') == 'Успешно'
