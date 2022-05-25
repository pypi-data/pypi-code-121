from apis_core.apis_labels.models import LabelType

nach_alt = LabelType.objects.filter(name__in=["alternative name", "alternativer Nachname"])
nach_ver = LabelType.objects.get(name="Nachname verheiratet")
nach_ver_alt = LabelType.objects.filter(name__in=["Nachname alternativ verheiratet", "Nachname alternativ vergeiratet"])
nach = []+list(nach_alt)+ list(nach_ver_alt)
nach.appen(nach_ver)
vor = LabelType.objects.get(name="alternativer Vorname")

nach = ["alternative name", "alternativer Nachname", "Nachname verheiratet", "Nachname alternativ verheiratet", "Nachname alternativ vergeiratet"]