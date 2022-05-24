"""
Utilities to localise the application.

author: Matthew Casey

&copy; [Digital Content Analysis Technology Ltd](https://www.d-cat.co.uk)
"""

import i18n


class Localise:
    """
    This class is used to set up all localisation for the SDK.
    """

    # Default and fallback locale.
    _DEFAULT_LOCALE = 'en_GB'
    _FALLBACK_LOCALE = 'en'

    @classmethod
    def setup(cls):
        """
        Sets up localisation so that the translations can be found and the defaults defined. Note that this assumes that the translations.py file has been built.
        """

        # Load in the string translations...
        import fusion_platform.translations

        # ...and set the configuration options.
        i18n.set('fallback', Localise._FALLBACK_LOCALE)
        i18n.set('error_on_missing_translation', True)
        i18n.set('error_on_missing_placeholder', True)
        i18n.set('error_on_missing_plural', True)
        i18n.set('enable_memoization', True)

    @classmethod
    def set_locale(cls, user_locale):
        """
        Sets the current locale.

        Args:
            user_locale: The locale to be used.
        """
        i18n.set('locale', user_locale)
