from telegram import (Update, ReplyKeyboardRemove)
from telegram.ext import (CallbackContext)
from digitalguide.pattern import JAHRESZAHL_PATTERN, KOMMAZAHL_PATTERN

from digitalguide.whatsapp.WhatsAppUpdate import WhatsAppUpdate
import re
import warnings

def telegram_eval_jahreszahl(update: Update, context: CallbackContext, echter_wert, richtig_text, vorher_singular_text, vorher_plural_text, spaeter_singular_text, spaeter_plural_text):
    echter_wert = int(echter_wert)
    schaetzung = int(re.findall(JAHRESZAHL_PATTERN, update.message.text)[0])
    if schaetzung == echter_wert:
        update.message.reply_text(richtig_text,
                                  reply_markup=ReplyKeyboardRemove())

    differenz = schaetzung - echter_wert
    if differenz == -1:
        update.message.reply_text(spaeter_singular_text,
                                  reply_markup=ReplyKeyboardRemove())
    elif differenz < -1:
        update.message.reply_text(spaeter_plural_text.format(abs(differenz)),
                                  reply_markup=ReplyKeyboardRemove())
    elif differenz == 1:
        update.message.reply_text(vorher_singular_text,
                                  reply_markup=ReplyKeyboardRemove())
    elif differenz > 1:
        update.message.reply_text(vorher_plural_text.format(abs(differenz)),
                                  reply_markup=ReplyKeyboardRemove())


def whatsapp_eval_jahreszahl(client, update: WhatsAppUpdate, context, echter_wert, richtig_text, vorher_singular_text, vorher_plural_text, spaeter_singular_text, spaeter_plural_text):
    echter_wert = int(echter_wert)
    schaetzung = int(re.findall(JAHRESZAHL_PATTERN, update.Body)[0])
    if schaetzung == echter_wert:
        client.messages.create(
            body=richtig_text,
            from_=update.To,
            to=update.From
        )

    differenz = schaetzung - echter_wert
    if differenz == -1:
        client.messages.create(
            body=spaeter_singular_text,
            from_=update.To,
            to=update.From
        )

    elif differenz < -1:
        client.messages.create(
            body=spaeter_plural_text.format(abs(differenz)),
            from_=update.To,
            to=update.From
        )

    elif differenz == 1:
        client.messages.create(
            body=vorher_singular_text,
            from_=update.To,
            to=update.From
        )

    elif differenz > 1:
        client.messages.create(
            body=vorher_plural_text.format(abs(differenz)),
            from_=update.To,
            to=update.From
        )


def telegram_eval_prozentzahl(update: Update, context: CallbackContext, echter_wert, richtig_text, falsch_text):
    warnings.warn("telegram_eval_prozentzahl is deprecated", DeprecationWarning)
    return telegram_eval_kommazahl(update, context, echter_wert, richtig_text, falsch_text, falsch_text, falsch_text, falsch_text)

def whatsapp_eval_prozentzahl(client, update: WhatsAppUpdate, context, echter_wert, richtig_text, falsch_text):
    warnings.warn("whatsapp_eval_prozentzahl is deprecated", DeprecationWarning)
    return whatsapp_eval_kommazahl(update, context, echter_wert, richtig_text, falsch_text, falsch_text, falsch_text, falsch_text)

def telegram_eval_kommazahl(update: Update, context: CallbackContext, echter_wert, richtig_text, vorher_singular_text, vorher_plural_text, spaeter_singular_text, spaeter_plural_text):
    echter_wert = float(echter_wert)
    match = re.search(
        KOMMAZAHL_PATTERN, update.message.text)

    if match:
        if match.group('vorkomma'):
            schaetzung = int(match.group('vorkomma'))
        else:
            schaetzung = 0

        if match.group('nachkomma'):
            schaetzung += float("0."+match.group('nachkomma'))

        if schaetzung == echter_wert:
            update.message.reply_text(richtig_text,
                                    reply_markup=ReplyKeyboardRemove())
        
        differenz = schaetzung - echter_wert
        if differenz == -1:
            update.message.reply_text(spaeter_singular_text,
                                    reply_markup=ReplyKeyboardRemove())
        elif differenz < -1:
            update.message.reply_text(spaeter_plural_text.format(abs(differenz)),
                                    reply_markup=ReplyKeyboardRemove())
        elif differenz == 1:
            update.message.reply_text(vorher_singular_text,
                                    reply_markup=ReplyKeyboardRemove())
        elif differenz > 1:
            update.message.reply_text(vorher_plural_text.format(abs(differenz)),
                                    reply_markup=ReplyKeyboardRemove())

def whatsapp_eval_kommazahl(client, update: WhatsAppUpdate, context, echter_wert, richtig_text, vorher_singular_text, vorher_plural_text, spaeter_singular_text, spaeter_plural_text):
    echter_wert = float(echter_wert)
    match = re.search(
        KOMMAZAHL_PATTERN, update.Body)

    if match:
        if match.group('vorkomma'):
            schaetzung = int(match.group('vorkomma'))
        else:
            schaetzung = 0

        if match.group('nachkomma'):
            schaetzung += float("0."+match.group('nachkomma'))

        if schaetzung == echter_wert:
            client.messages.create(
                body=richtig_text,
                from_=update.To,
                to=update.From
            )

        differenz = schaetzung - echter_wert
        if differenz == -1:
            client.messages.create(
                body=spaeter_singular_text,
                from_=update.To,
                to=update.From
            )

        elif differenz < -1 or (-1 < differenz < 0):
            client.messages.create(
                body=spaeter_plural_text.format(abs(differenz)),
                from_=update.To,
                to=update.From
            )

        elif differenz == 1:
            client.messages.create(
                body=vorher_singular_text,
                from_=update.To,
                to=update.From
            )

        elif differenz > 1 or (0 < differenz < 1):
            client.messages.create(
                body=vorher_plural_text.format(abs(differenz)),
                from_=update.To,
                to=update.From
            )

def telegram_eval_laenge(update: Update, context: CallbackContext, echter_wert, richtig_text, vorher_singular_text, vorher_plural_text, spaeter_singular_text, spaeter_plural_text):
    warnings.warn("telegram_eval_laenge is deprecated", DeprecationWarning)
    return telegram_eval_kommazahl(update, context, echter_wert, richtig_text, vorher_singular_text, vorher_plural_text, spaeter_singular_text, spaeter_plural_text)

def whatsapp_eval_laenge(client, update: WhatsAppUpdate, context, echter_wert, richtig_text, vorher_singular_text, vorher_plural_text, spaeter_singular_text, spaeter_plural_text):
    warnings.warn("whatsapp_eval_laenge is deprecated", DeprecationWarning)
    return whatsapp_eval_kommazahl(client, update, context, echter_wert, richtig_text, vorher_singular_text, vorher_plural_text, spaeter_singular_text, spaeter_plural_text)

telegram_action_functions = {"eval_jahreszahl": telegram_eval_jahreszahl,
                             "eval_prozentzahl": telegram_eval_prozentzahl,
                             "eval_kommazahl": telegram_eval_kommazahl,
                             "eval_laenge": telegram_eval_laenge,
                             }

whatsapp_action_functions = {"eval_jahreszahl": whatsapp_eval_jahreszahl,
                             "eval_prozentzahl": whatsapp_eval_prozentzahl,
                             "eval_kommazahl": whatsapp_eval_kommazahl,
                             "eval_laenge": whatsapp_eval_laenge,
                             }
