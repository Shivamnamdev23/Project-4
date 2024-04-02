import requests
import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from bot import Bot
from config import ADMINS, CHANNEL_ID, DISABLE_CHANNEL_BUTTON
from helper_func import encode
from pymongo import MongoClient

mongo_client = MongoClient("mongodb+srv://FilesharingBot:FilesharingBot@cluster0.r6bvmvj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = mongo_client["url_shortener"]
user_collection = db["usersx"]

@Bot.on_message(filters.private & filters.user(ADMINS) & ~filters.command(['start','users','broadcast','batch','genlink','stats']))
async def channel_post(bot: Bot, message: Message):
    if message.text.startswith("/"):
        return
    reply_text = await message.reply_text("Please Wait...!", quote=True)
    try:
        post_message = await message.copy(chat_id=bot.db_channel.id, disable_notification=True)
    except FloodWait as e:
        await asyncio.sleep(e.x)
        post_message = await message.copy(chat_id=bot.db_channel.id, disable_notification=True)
    except Exception as e:
        print(e)
        await reply_text.edit_text("Something went Wrong..!")
        return

    converted_id = post_message.message_id * abs(bot.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://telegram.me/{bot.username}?start={base64_string}"

    # Retrieve URL and API key from the database
    user_data = user_collection.find_one({"user_id": message.from_user.id})
    if user_data and "shortner_url" in user_data and "shortner_api" in user_data:
        shortner_url = user_data["shortner_url"]
        shortner_api = user_data["shortner_api"]

        # Use URL and API key to generate short link
        short_link = await get_short_link(shortner_url, shortner_api, link)
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
        
async def get_short_link(shortner_url, shortner_api, link):
    try:
        response = requests.get(f"{shortner_url}?api_key={shortner_api}&url={link}")
        data = response.json()
        if response.status_code == 200 and data.get("status") == "success":
            return data.get("shortened_url")
        else:
            return None
    except Exception as e:
        print(f"Error occurred while shortening URL: {e}")
        return None
        
@Bot.on_message(filters.private & filters.command("set_shortner"))
async def set_shortner_api(bot: Bot, message: Message):
    await message.reply_text("<b>Sᴇɴᴅ ᴍᴇ ᴀ sʜᴏʀᴛʟɪɴᴋ ᴜʀʟ...</b>\n\n/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪs ᴘʀᴏᴄᴇss.", parse_mode="html")
    url_msg = await bot.listen(message.from_user.id)
    if url_msg.text == '/cancel':
        await message.reply("ᴄᴀɴᴄᴇʟʟᴇᴅ ᴛʜɪs ᴘʀᴏᴄᴇss...")
        return
    url = url_msg.text
    await url_msg.delete()

    await message.reply("sᴇɴᴅ ᴍᴇ sʜᴏʀᴛʟɪɴᴋ ᴀᴘɪ...")
    api_msg = await bot.listen(message.from_user.id)
    if api_msg.text == '/cancel':
        await message.reply("ᴄᴀɴᴄᴇʟʟᴇᴅ ᴛʜɪs ᴘʀᴏᴄᴇss...")
        return
    api_key = api_msg.text
    await api_msg.delete()

    # Now you have both URL and API, save them to the database
    user_collection.update_one(
        {"user_id": message.from_user.id},
        {"$set": {"shortner_url": url, "shortner_api": api_key}},
        upsert=True
    )
    await message.reply_text("URL shortener and API key saved successfully!")
