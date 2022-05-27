
from telegram import (ReplyKeyboardRemove, Update)
from telegram.ext import (CallbackContext)

from digitalguide.whatsapp.WhatsAppUpdate import WhatsAppUpdate

def telegram_loop_list(update: Update, context: CallbackContext, key, value, doppelte_antwort):
    if not key in context.user_data:
        context.user_data[key] = []

    if value in context.user_data[key]:
        update.message.reply_text(doppelte_antwort,
                                    reply_markup=ReplyKeyboardRemove())
        return "{}_FRAGE".format(key.upper())
    else:
        context.user_data[key].append(value)

def telegram_loop_list_fertig(update: Update, context: CallbackContext, key, answer_id_list, fertig_antwort):
    if set(answer_id_list).issubset(set(context.user_data[key])):
        update.message.reply_text(fertig_antwort,
                                    reply_markup=ReplyKeyboardRemove())


def whatsapp_loop_list(client, update: WhatsAppUpdate, context,  key, value, doppelte_antwort):
    if not key in context:
        context[key] = []

    if value in context[key]:
        client.messages.create(
            body=doppelte_antwort,
            from_=update.To,
            to=update.From
        )
        return "{}_FRAGE".format(key.upper())
    else:
        context[key].append(value)

def whatsapp_loop_list_fertig(client, update, context, key, answer_id_list, fertig_antwort):
    if set(answer_id_list).issubset(set(context[key])):
        client.messages.create(
            body=fertig_antwort,
            from_=update.To,
            to=update.From
        )

def telegram_eval_list(update: Update, context: CallbackContext, answer_id_name_list, poi, response_text):
    if not poi in context.user_data:
        context.user_data[poi] = []

    response_text += "\n"

    for id, name in answer_id_name_list:
        if id in context.user_data[poi]:
            response_text += "✅ {}\n".format(name)
        else:
            response_text += "◽ {}\n".format(name)

    update.message.reply_text(response_text,
                              reply_markup=ReplyKeyboardRemove())


def whatsapp_eval_list(client, update: WhatsAppUpdate, context, answer_id_name_list, poi, response_text):
    if not poi in context:
        context[poi] = []

    response_text += "\n"

    for id, name in answer_id_name_list:
        if id in context[poi]:
            response_text += "✅ {}\n".format(name)
        else:
            response_text += "◽ {}\n".format(name)

    client.messages.create(
        body=response_text,
        from_=update.To,
        to=update.From
    )


telegram_action_functions = {"loop_list": telegram_loop_list,
                             "eval_list": telegram_eval_list,
                             "loop_list_fertig": telegram_loop_list_fertig
                             }

whatsapp_action_functions = {"loop_list": whatsapp_loop_list,
                             "eval_list": whatsapp_eval_list,
                             "loop_list_fertig": whatsapp_loop_list_fertig
                             }
