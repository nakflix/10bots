
from pyrogram import __version__
from levi import Bot
from config import OWNER_ID
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "about":
        await query.message.edit_text(
            text = f"<b><b>○ ɴᴀᴋғʟɪxᴛᴠ : <a href='https://t.me/NAKFLIXTV'>ɴᴀᴋғʟɪx ᵗᵛ—͟͟͞͞𖣘</a>\n○ ɴᴀᴋғʟɪxᴘʟᴜs : <a href='https://t.me/NAKFLIXPLUS'>ɴᴀᴋғʟɪx ᵖˡᵘˢ—͟͟͞͞𖣘</a>\n○ ᴍᴏᴠɪᴇs/sᴇʀɪᴇs : <a href='https://t.me/+r9GjnKf7fnEzOWJk'>ɴᵃᵏᶠˡⁱˣ ʀᵉᵠᵘᵉˢᵗˢ ɢʳᵒᵘᵖ—͟͟͞͞𖣘</a>\n○ Yᴏᴜᴛᴜʙᴇ : <a href='https://youtube.com/c/Nakflix'>ᴍᴏᴠɪᴇs ᴀɴᴅ sᴇʀɪᴇs ʀᴇᴄᴏᴍᴍᴇɴᴅᴀᴛɪᴏɴs</a>\n○ Wʜᴀᴛsᴀᴘᴘ : <a href='https://whatsapp.com/channel/0029VaylzSr2v1ImsNFovD2v'>ɴᴇᴡs ᴜᴘᴅᴀᴛᴇs ᴀɴᴅ ᴍᴏʀᴇ</a>\n○ Iɴsᴛᴀɢʀᴀᴍ : <a href='https://instagram.com/nakflixtv'>ғᴏʟʟᴏᴡ</a></b>",
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                    InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data = "close")
                    ]
                ]
            )
        )
    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass
