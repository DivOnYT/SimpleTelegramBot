from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, filters, MessageHandler

# Replace 'YOUR_TOKEN' with your actual bot token
YOUR_TOKEN = 'YOUR APP TOKEN' # Your App Token

groups = ["GROUPS IDS"] # Your groups id

authorized_admins = ["USER IDS"] # Authorized Users ID for admins of the group

banned_words = ["spam", "Coco"]

warned_users = {}


async def get_admins(chat_id, context):
    administrators = await context.bot.get_chat_administrators(chat_id)

    admin_info = []
    for admin in administrators:
        admin_info.append(admin.user.id)

    return admin_info
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Welcome to the Telegram Group Management Bot!')

async def ban(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id


    if chat_id in groups and user_id in get_admins(chat_id, context):
        if update.message.reply_to_message is not None and update.message.reply_to_message.from_user is not None:
            banned_user_id = update.message.reply_to_message.from_user.id
            await context.bot.ban_chat_member(chat_id, banned_user_id)
            await update.message.reply_text('User banned from this group')
        else:
            await update.message.reply_text('Please reply to a user\'s message to ban them')
    else:
        await update.message.reply_text('You are not authorized to use this command in this group')


async def unban(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    user_id = update.message.reply_to_message.from_user.id
    executor_id = update.message.from_user.id

    if chat_id in groups and executor_id in get_admins(chat_id, context):
        if chat_id in groups:
            await context.bot.unban_chat_member(chat_id, user_id)
            await update.message.reply_text(f'You have successfully unbanned {update.message.from_user.username} from the Group')
        else:
            await update.message.reply_text('Please reply to a user\'s message to unban them')
    else:
        await update.message.reply_text('You are not authorized to use this command in this group')


async def broadcast(update: Update, context: CallbackContext) -> None:
    message = ' '.join(context.args)

    if message.strip() != '':
        for group in groups:
            await context.bot.send_message(chat_id=group, text=message)
    else:
        await update.message.reply_text('Please provide a non-empty message for broadcasting.')


async def spam_control(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    if chat_id in groups:
        for word in banned_words:
            if word in update.message.text.lower():
                # Supprimer le message du spammeur
                await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)

                warn(update, context) # warn the people

                # Avertir l'utilisateur du spam
                await update.message.reply_text('Please refrain from spamming. You have been Warned.')

def warn(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    if warned_users.get(user_id) is not None:
        warned_users[user_id] = warned_users[user_id] +1
    else:
        warned_users[user_id] = 1


def main() -> None:
    application = Application.builder().token(YOUR_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('ban', ban))
    application.add_handler(CommandHandler('unban', unban))
    application.add_handler(CommandHandler('broadcast', broadcast))

    message_handler = MessageHandler(filters.TEXT, spam_control)
    application.add_handler(message_handler)

    application.run_polling()
    application.idle()


if __name__ == '__main__':
    main()