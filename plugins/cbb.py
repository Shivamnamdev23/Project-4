# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper




from pyrogram import __version__
from bot import Bot
from config import OWNER_ID
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery



@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "about":
        await query.message.edit_text(
            text = f"<b>My Name : <a href='https://t.me/OTT_Provider_Bot'> OTT Provider Bot </a> \n📢 My Channel : <a href='https://t.me/OTTProvider'>OTT_Provider</a> \n😎 My Owner : <a href='t.me/OTTProviderBackup'> ⏤͟͞𝗦𝗛𝗜𝗕𝗔𝗠 » 𝗦𝗔𝗛∆ </a>\n🧑‍💻 Developer : <a href='t.me/Crazybotz'> Crazy </a></b>",
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [ [ InlineKeyboardButton("Official Channel", url="https://t.me/OTTProvider") ],
                    [
                        InlineKeyboardButton("🔒 Close", callback_data = "close")
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





# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper
