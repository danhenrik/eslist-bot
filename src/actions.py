import telegram
from telegram.ext import ConversationHandler

(SELECTING_ACTION, RESTART) = map(chr, range(2))

""" Módulo com "funções comportamentais" do bot """

# Função simples para enviar uma mensagem


def say(update, context, message):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=message
    )
