


import os
import asyncio
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

from levi import Bot
from config import ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT
from helper_func import subscribed, encode, decode, get_messages, get_unjoined_channels
from database.database import add_user, del_user, full_userbase, present_user




@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    id = message.from_user.id
    if not await present_user(id):
        try:
            await add_user(id)
        except:
            pass
    text = message.text
    if len(text)>7:
        try:
            base64_string = text.split(" ", 1)[1]
        except:
            return
        string = await decode(base64_string)
        argument = string.split("-")
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
            except:
                return
            if start <= end:
                ids = range(start,end+1)
            else:
                ids = []
                i = start
                while True:
                    ids.append(i)
                    i -= 1
                    if i < end:
                        break
        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except:
                return
        temp_msg = await message.reply("Please Wait a While....")
        try:
            messages = await get_messages(client, ids)
        except:
            await message.reply_text("Something went wrong..!")
            return
        await temp_msg.delete()

        for msg in messages:

            if bool(CUSTOM_CAPTION) & bool(msg.document):
                caption = CUSTOM_CAPTION.format(previouscaption = "" if not msg.caption else msg.caption.html, filename = msg.document.file_name)
            else:
                caption = "" if not msg.caption else msg.caption.html

            if DISABLE_CHANNEL_BUTTON:
                reply_markup = msg.reply_markup
            else:
                reply_markup = None

            try:
                await msg.copy(chat_id=message.from_user.id, caption = caption, parse_mode = ParseMode.HTML, reply_markup = reply_markup, protect_content=PROTECT_CONTENT)
                await asyncio.sleep(0.5)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await msg.copy(chat_id=message.from_user.id, caption = caption, parse_mode = ParseMode.HTML, reply_markup = reply_markup, protect_content=PROTECT_CONTENT)
            except:
                pass
        return
    else:
        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("😊 About Me", callback_data = "about"),
                    InlineKeyboardButton("🔒 Close", callback_data = "close")
                ]
            ]
        )
        await message.reply_text(
            text = START_MSG.format(
                first = message.from_user.first_name,
                last = message.from_user.last_name,
                username = None if not message.from_user.username else '@' + message.from_user.username,
                mention = message.from_user.mention,
                id = message.from_user.id
            ),
            reply_markup = reply_markup,
            disable_web_page_preview = True,
            quote = True
        )
        return

WAIT_MSG = """"<b>Processing ...</b>"""

REPLY_ERROR = """<code>Use this command as a replay to any telegram message with out any spaces.</code>"""





@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    user_id = message.from_user.id

    # Find which channels the user has NOT joined
    unjoined = await get_unjoined_channels(client, user_id)

    # Map channel IDs to their invite links and labels
    channel_map = {}
    from config import FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2, FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4
    if FORCE_SUB_CHANNEL_1:
        channel_map[FORCE_SUB_CHANNEL_1] = ("➥ Join Channel 1️⃣", client.invitelink)
    if FORCE_SUB_CHANNEL_2:
        channel_map[FORCE_SUB_CHANNEL_2] = ("➥ Join Channel 2️⃣", client.invitelink2)
    if FORCE_SUB_CHANNEL_3:
        channel_map[FORCE_SUB_CHANNEL_3] = ("➥ Join Channel 3️⃣", client.invitelink3)
    if FORCE_SUB_CHANNEL_4:
        channel_map[FORCE_SUB_CHANNEL_4] = ("➥ Join Channel 4️⃣", client.invitelink4)

    # Build channel name list for the message
    unjoined_names = []
    join_buttons = []
    for ch_id in unjoined:
        if ch_id in channel_map:
            label, link = channel_map[ch_id]
            unjoined_names.append(label.replace("➥ ", ""))
            join_buttons.append(InlineKeyboardButton(text=label, url=link))

    # Pair join buttons in rows of 2
    buttons = []
    for i in range(0, len(join_buttons), 2):
        row = join_buttons[i:i+2]
        buttons.append(row)

    # Try Again button
    try:
        buttons.append(
            [
                InlineKeyboardButton(
                    text='♻️ ❙❙ Try Again ❙❙ ♻️',
                    url=f"https://t.me/{client.username}?start={message.command[1]}"
                )
            ]
        )
    except IndexError:
        buttons.append(
            [
                InlineKeyboardButton(
                    text='♻️ ❙❙ Try Again ❙❙ ♻️',
                    url=f"https://t.me/{client.username}?start"
                )
            ]
        )

    # Build message text listing which channels are still not joined
    not_joined_text = "\n".join([f"• {name}" for name in unjoined_names])
    force_text = (
        f"<b>Hello👋 {message.from_user.mention}</b>\n\n"
        f"⚠️ You have <b>not subscribed</b> to the following required channel(s):\n\n"
        f"{not_joined_text}\n\n"
        f"Please join them and press <b>♻️ Try Again ♻️</b> to continue. 👇"
    )

    await message.reply(
        text=force_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True,
        disable_web_page_preview=True
    )

@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text=WAIT_MSG)
    users = await full_userbase()
    await msg.edit(f"{len(users)} users are using this bot")

@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if message.reply_to_message:
        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0

        pls_wait = await message.reply("<i>Broadcasting Message.. This will Take Some Time</i>")
        for chat_id in query:
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.copy(chat_id)
                successful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except:
                unsuccessful += 1
                pass
            total += 1

        status = f"""<b><u>Broadcast Completed</u>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""

        return await pls_wait.edit(status)

    else:
        msg = await message.reply(REPLY_ERROR)
        await asyncio.sleep(8)
        await msg.delete()


@Bot.on_message(filters.private & filters.command('pin') & filters.user(ADMINS), group=-1)
async def pin_broadcast(client: Bot, message: Message):
    if not message.reply_to_message:
        await message.reply(
            "<b>📌 How to use /pin:</b>\n\n"
            "1. Type your announcement message and send it to me\n"
            "2. Reply to that message with /pin\n\n"
            "<i>The bot will forward it to all users and pin it in their chat.</i>"
        )
        return

    query = await full_userbase()
    broadcast_msg = message.reply_to_message
    total = 0
    successful = 0
    blocked = 0
    deleted = 0
    unsuccessful = 0

    pls_wait = await message.reply("<i>📌 Pinning Message to all users... This will Take Some Time</i>")

    for chat_id in query:
        try:
            sent = await broadcast_msg.copy(chat_id=chat_id)
            await client.pin_chat_message(chat_id=chat_id, message_id=sent.id, disable_notification=False)
            successful += 1
        except FloodWait as e:
            await asyncio.sleep(e.x)
            try:
                sent = await broadcast_msg.copy(chat_id)
                await client.pin_chat_message(chat_id=chat_id, message_id=sent.id, disable_notification=False)
                successful += 1
            except:
                unsuccessful += 1
        except UserIsBlocked:
            await del_user(chat_id)
            blocked += 1
        except InputUserDeactivated:
            await del_user(chat_id)
            deleted += 1
        except:
            unsuccessful += 1
        total += 1

    status = f"""<b><u>📌 Pin Broadcast Completed</u>

Total Users: <code>{total}</code>
Successfully Pinned: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""

    return await pls_wait.edit(status)


@Bot.on_message(filters.private & filters.command('unpin') & filters.user(ADMINS), group=-1)
async def unpin_broadcast(client: Bot, message: Message):
    query = await full_userbase()
    total = 0
    successful = 0
    blocked = 0
    deleted = 0
    unsuccessful = 0

    pls_wait = await message.reply("<i>📌 Unpinning messages from all users... This will Take Some Time</i>")

    for chat_id in query:
        try:
            await client.unpin_all_chat_messages(chat_id=chat_id)
            successful += 1
        except FloodWait as e:
            await asyncio.sleep(e.x)
            try:
                await client.unpin_all_chat_messages(chat_id=chat_id)
                successful += 1
            except:
                unsuccessful += 1
        except UserIsBlocked:
            await del_user(chat_id)
            blocked += 1
        except InputUserDeactivated:
            await del_user(chat_id)
            deleted += 1
        except:
            unsuccessful += 1
        total += 1

    status = f"""<b><u>📌 Unpin Broadcast Completed</u>

Total Users: <code>{total}</code>
Successfully Unpinned: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""

    return await pls_wait.edit(status)
