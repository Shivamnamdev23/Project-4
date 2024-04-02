import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from bot import Bot
from config import ADMINS, CHANNEL_ID, DISABLE_CHANNEL_BUTTON
from helper_func import encode, get_short_link
from database.database import get_user_data

@Bot.on_message(filters.private & filters.user(ADMINS) & ~filters.command(['start','users','broadcast','batch','genlink','stats']))
async def channel_post(client: Client, message: Message):
    reply_text = await message.reply_text("Please Wait...!", quote=True)
    try:
        post_message = await message.copy(chat_id=client.db_channel.id, disable_notification=True)
    except FloodWait as e:
        await asyncio.sleep(e.x)
        post_message = await message.copy(chat_id=client.db_channel.id, disable_notification=True)
    except Exception as e:
        print(e)
        await reply_text.edit_text("Something went Wrong..!")
        return

    converted_id = post_message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://telegram.me/{client.username}?start={base64_string}"

    # Retrieve user-specific data (API key, shortening site, etc.) here
    user = await get_user_data(message.from_user.id)
    if user:
        # Shorten the link using user-specific data
        short_link = await get_short_link(user, link)
        if short_link:
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("📁 File Link", url=short_link),
                 InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={short_link}')]])
            await reply_text.edit(
                f"<b>✅ Your <a href='{short_link}'>Link</a> has been generated!\n\n👇 You can access the file using the link below.\n\n<code>{short_link}</code>\n(👆 Tap to copy)</b>",
                reply_markup=reply_markup, disable_web_page_preview=True)
            if not DISABLE_CHANNEL_BUTTON:
                await post_message.edit_reply_markup(reply_markup)
        else:
            # Fallback to the original link if shortening failed
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("📁 Original File Link", url=link),
                 InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
            await reply_text.edit(
                f"<b>⚠️ Failed to generate a short link.\n\n👇 You can access the file using the original link below.\n\n<code>{link}</code>\n(👆 Tap to copy)</b>",
                reply_markup=reply_markup, disable_web_page_preview=True)
    else:
        await reply_text.edit_text("User data not found. Please make sure the user data is stored correctly.")
        
@Bot.on_message(filters.channel & filters.incoming & filters.chat(CHANNEL_ID))
async def new_post(client: Client, message: Message):
    if DISABLE_CHANNEL_BUTTON:
        return
    converted_id = message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    try:
        await message.edit_reply_markup(reply_markup)
    except Exception as e:
        print(e)
        pass
