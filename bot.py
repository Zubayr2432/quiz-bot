import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
    ReplyKeyboardRemove,
    ForceReply
)

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from datetime import datetime
from aiogram.filters import StateFilter
import random
import string
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F, exceptions
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties  # <-- Yangi import

# Konfiguratsiya
class Config:
    CHANNEL_USERNAME = "ajoyib_kino_kodlari1"
    CHANNEL_LINK = f"https://t.me/ajoyib_kino_kodlari1"
    CHANNEL_ID = -1002341118048
    
    SECRET_CHANNEL_USERNAME = "maxfiy_kino_kanal"
    SECRET_CHANNEL_LINK = f"https://t.me/maxfiy_kino_kanal"
    SECRET_CHANNEL_ID = -1002537276349
    
    BOT_TOKEN = "7808158374:AAGMY8mkb0HVi--N2aJyRrPxrjotI6rnm7k"
    ADMIN_IDS = [7871012050, 7183540853]

# Botni yangi usulda ishga tushirish
bot = Bot(
    token=Config.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)  # <-- Yangi usul
)
dp = Dispatcher()  # <-- Dispatcherga bot parametrini bermaslik

current_movie_id = 100  # 100 dan boshlab raqamlash
movies_db = {}  # Kino ma'lumotlari bazasi

# Kod generatsiya funksiyasi
def generate_movie_code():
    """Avtomatik ravishda ketma-ket raqamli kod generatsiya qilish"""
    global current_movie_id
    code = str(current_movie_id)
    current_movie_id += 1
    return code

# Ma'lumotlar bazasi (vaqtincha)
user_data = set()
movies_db = {}
current_movie_id = 1

# Logging sozlamalari
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Obunani tekshirish funksiyasi
async def check_subscription(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(Config.CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Obunani tekshirishda xato: {e}")
        return False

async def ask_for_subscription(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="📢 Kanalga o'tish", url=Config.CHANNEL_LINK)
    builder.button(text="✅ Obuna bo'ldim", callback_data="check_subscription")
    builder.adjust(1)

    await message.answer(
        "🤖 Botdan to'liq foydalanish uchun quyidagi kanalga obuna bo'ling:\n"
        f"{Config.CHANNEL_LINK}\n\n"
        "Obuna bo'lgach, '✅ Obuna bo'ldim' tugmasini bosing.",
        reply_markup=builder.as_markup(),
        disable_web_page_preview=True
    )

@dp.callback_query(F.data == "check_subscription")
async def verify_subscription(query: types.CallbackQuery):
    if await check_subscription(query.from_user.id):
        try:
            await query.message.delete()
        except Exception as e:
            logger.warning(f"Xabarni o'chirishda xato: {e}")
        
        await query.answer("✅ Obuna tasdiqlandi!", show_alert=True)
        await start_cmd(query.message)
    else:
        await query.answer("❌ Obuna tasdiqlanmadi!", show_alert=True)

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user = message.from_user
    user_data.add(user.id)
    
    if not await check_subscription(user.id):
        await ask_for_subscription(message)
        return
    
    builder = ReplyKeyboardBuilder()
    builder.button(text="📞 Adminga murojaat")
    
    await message.answer(
        f"👋 Salom, {user.full_name}!\n\n"
        "🎥 Kino kodini yuboring yoki admin paneliga kirish uchun /admin buyrug'ini yuboring.",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )

# Admin paneli
@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id not in Config.ADMIN_IDS:
        await message.answer("❌ Siz admin emassiz!")
        return

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎬 Kino qo'shish")],
            [KeyboardButton(text="❌ Kino o'chirish")],
            [KeyboardButton(text="📊 Statistika")],
            [KeyboardButton(text="📢 Reklama yuborish")],
            [KeyboardButton(text="🏠 Asosiy menyu")]
        ],
        resize_keyboard=True,
    )

    await message.answer("👋 Admin paneliga xush kelibsiz!", reply_markup=keyboard)
# Kino qo'shish holati
class MovieStates(StatesGroup):
    waiting_for_title = State()  # Kino nomini kutish holati
    waiting_for_file = State()   # Kino faylini kutish holati

# Kino qo'shishni boshlash
@dp.message(F.text == "🎬 Kino qo'shish")
async def start_adding_movie(message: Message, state: FSMContext):
    if message.from_user.id not in Config.ADMIN_IDS:
        await message.answer("❌ Sizda bunday huquq yo'q!")
        return
    
    await message.answer(
        "📝 Kino nomini kiriting:",
        reply_markup=ReplyKeyboardRemove()  # Barcha tugmalarni olib tashlash
    )
    await state.set_state(MovieStates.waiting_for_title)

# Kino nomi qabul qilish
@dp.message(MovieStates.waiting_for_title)
async def process_movie_title(message: Message, state: FSMContext):
    if len(message.text) > 100:
        await message.answer("❌ Kino nomi juda uzun! Iltimos, qisqaroq nom yuboring.")
        return
        
    movie_code = generate_movie_code()  # Avtomatik kod generatsiya
    
    await state.update_data(
        movie_title=message.text,
        movie_code=movie_code
    )
    
    await message.answer(
        f"✅ Kino nomi: {message.text}\n"
        f"🔢 Avtomatik kod: {movie_code}\n\n"
        "📤 Kino faylini yuboring (video yoki dokument):",
        reply_markup=ReplyKeyboardRemove()  # Barcha tugmalarni olib tashlash
    )
    await state.set_state(MovieStates.waiting_for_file)

# Kino faylini qabul qilish
@dp.message(MovieStates.waiting_for_file, F.video | F.document)
async def handle_movie_file(message: Message, state: FSMContext):
    data = await state.get_data()
    movie_title = data['movie_title']
    movie_code = data['movie_code']
    
    if message.video:
        file = message.video
        file_type = "video"
    else:
        file = message.document
        file_type = "document"
    
    try:
        if file_type == "video":
            sent_msg = await bot.send_video(
                chat_id=Config.SECRET_CHANNEL_ID,
                video=file.file_id,
                caption=f"🎬 {movie_title}\n🔐 Kodi: {movie_code}"
            )
        else:
            sent_msg = await bot.send_document(
                chat_id=Config.SECRET_CHANNEL_ID,
                document=file.file_id,
                caption=f"📄 {movie_title}\n🔐 Kodi: {movie_code}"
            )
        
        # Bazaga saqlash
        movies_db[movie_code] = {
            "title": movie_title,
            "file_id": file.file_id,
            "file_type": file_type,
            "code": movie_code,
            "message_id": sent_msg.message_id,
            "date_added": datetime.now().strftime('%Y-%m-%d %H:%M'),
            "added_by": message.from_user.id
        }
        
        await message.answer(
            f"✅ Kino muvaffaqiyatli qo'shildi!\n\n"
            f"📌 Nomi: {movie_title}\n"
            f"🔢 Kodi: {movie_code}"
        )
        
    except Exception as e:
        logger.error(f"Kino qo'shishda xato: {e}")
        await message.answer("❌ Kino yuklashda xatolik yuz berdi!")
    
    await state.clear()

# Kino o'chirish funksiyalari
@dp.message(F.text == "❌ Kino o'chirish")
async def start_removing_movie(message: Message):
    """Admin uchun kinolarni o'chirish menyusini ko'rsatish"""
    if message.from_user.id not in Config.ADMIN_IDS:
        await message.answer("❌ Sizda bunday huquq yo'q!")
        return
    
    if not movies_db:
        await message.answer("⚠️ Hozircha bazada hech qanday kino mavjud emas!")
        return
    
    # Kino ro'yxatini chiroyli shaklda tayyorlash
    movies_list = "\n".join(
        [f"🎬 {id}: {data['caption'][:30]}..." if len(data['caption']) > 30 
         else f"🎬 {id}: {data['caption']}" 
         for id, data in movies_db.items()]
    )
    
    await message.answer(
        f"<b>🗑 Kino o'chirish</b>\n\n"
        f"Quyidagi kinolardan birining raqamini yuboring:\n\n"
        f"{movies_list}\n\n"
        f"<i>❗ Diqqat: Kino kanaldan ham o'chib ketadi!</i>",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🔙 Orqaga")]],
            resize_keyboard=True
        ),
        parse_mode="HTML"
    )

@dp.message(F.from_user.id.in_(Config.ADMIN_IDS) & F.text.regexp(r'^\d+$'))
async def remove_movie(message: Message):
    """Kino ni bazadan va kanaldan o'chirish"""
    movie_id = message.text.strip()
    
    # Kino mavjudligini tekshirish
    if movie_id not in movies_db:
        await message.answer(
            "❌ Bunday raqamdagi kino topilmadi!\n"
            "Iltimos, kino raqamini qayta tekshiring.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="🔙 Orqaga")]],
                resize_keyboard=True
            )
        )
        return
    
    movie_data = movies_db[movie_id]
    
    try:
        # Kino ni kanaldan o'chirish
        await bot.delete_message(
            chat_id=Config.SECRET_CHANNEL_ID,
            message_id=movie_data["message_id"]
        )
        
        # Kino ni bazadan o'chirish
        del movies_db[movie_id]
        
        # Muvaffaqiyatli xabar
        await message.answer(
            f"✅ <b>Kino #{movie_id} muvaffaqiyatli o'chirildi!</b>\n\n"
            f"📌 Nomi: {movie_data['caption']}\n"
            f"🗓 Bazadan o'chirildi: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="🏠 Admin panel")]],
                resize_keyboard=True
            ),
            parse_mode="HTML"
        )
        
    except exceptions.TelegramBadRequest as e:
        logger.error(f"Kino o'chirishda xato (TelegramBadRequest): {e}")
        await message.answer(
            "❌ Kino kanaldan o'chirishda xatolik yuz berdi.\n"
            "Ehtimol, kino allaqachon o'chirilgan yoki botda huquqlar yetarli emas."
        )
        
    except Exception as e:
        logger.error(f"Kino o'chirishda xato: {e}", exc_info=True)
        await message.answer(
            "❌ Kino o'chirishda kutilmagan xatolik yuz berdi.\n"
            "Iltimos, texnik yordamga murojaat qiling."
        )






# Foydalanuvchilarga kinolarni yuborish (maxfiy kanaldan)
@dp.message(F.text.regexp(r'^\d+$') & ~F.from_user.id.in_(Config.ADMIN_IDS))
async def send_movie_to_user(message: Message):
    movie_code = message.text.strip()
    
    # Obunani tekshirish
    if not await check_subscription(message.from_user.id):
        await ask_for_subscription(message)
        return
    
    # Kino bazada mavjudligini tekshirish
    if movie_code not in movies_db:
        await message.answer("❌ Bunday kodli kino topilmadi!")
        return
    
    movie = movies_db[movie_code]
    
    try:
        # Maxfiy kanaldan faylni forward qilish
        if movie["file_type"] == "video":
            await bot.forward_message(
                chat_id=message.chat.id,
                from_chat_id=Config.SECRET_CHANNEL_ID,
                message_id=movie["message_id"]
            )
        else:
          await bot.send_video(
    chat_id=message.chat.id,
    video=movies_db[movie_code]["file_id"],
    caption=f"🎬 {movies_db[movie_code]['title']}"
)
        # Yoki copy_message metodi bilan (agar forward ko'rinmasin)
        # await bot.copy_message(
        #     chat_id=message.chat.id,
        #     from_chat_id=Config.SECRET_CHANNEL_ID,
        #     message_id=movie["message_id"]
        # )
        
    except exceptions.TelegramForbiddenError:
        await message.answer("❌ Kino yuborish mumkin emas. Botga kanalda admin huquqlarini tekshiring.")
    except exceptions.TelegramBadRequest:
        await message.answer("❌ Kino topilmadi. Adminlarga murojaat qiling.")
    except Exception as e:
        logger.error(f"Kino yuborishda xato: {e}")
        await message.answer("❌ Texnik xatolik yuz berdi. Iltimos, keyinroq urunib ko'ring.")





# Qolgan funksiyalar (adminga murojaat, statistika, reklama)
@dp.message(F.text == "📞 Adminga murojaat")
async def contact_admin(message: Message):
    await message.answer(
        "✍️ Adminga xabar yuborish uchun matn, rasm, video yoki fayl yuboring.\n\n"
        "Yoki to'g'ridan-to'g'ri @admin ga yozishingiz mumkin.",
        reply_markup=ReplyKeyboardRemove()
    )

@dp.message(F.chat.type == "private", ~F.from_user.id.in_(Config.ADMIN_IDS))
async def user_to_admin(message: Message):
    try:
        user_info = (
            f"👤 Foydalanuvchi: {message.from_user.full_name}\n"
            f"🆔 ID: {message.from_user.id}\n"
            f"📅 Sana: {message.date.strftime('%Y-%m-%d %H:%M')}\n\n"
        )
        
        if message.text:
            caption = f"{user_info}📝 Xabar: {message.text}"
            for admin_id in Config.ADMIN_IDS:
                await bot.send_message(admin_id, caption, reply_markup=ForceReply())
        
        elif message.photo:
            caption = f"{user_info}📷 Rasm"
            for admin_id in Config.ADMIN_IDS:
                await bot.send_photo(admin_id, message.photo[-1].file_id, 
                                   caption=caption, 
                                   reply_markup=ForceReply())
        
        elif message.video:
            caption = f"{user_info}🎥 Video"
            for admin_id in Config.ADMIN_IDS:
                await bot.send_video(admin_id, message.video.file_id, 
                                   caption=caption, 
                                   reply_markup=ForceReply())
        
        elif message.document:
            caption = f"{user_info}📄 Fayl: {message.document.file_name}"
            for admin_id in Config.ADMIN_IDS:
                await bot.send_document(admin_id, message.document.file_id, 
                                      caption=caption, 
                                      reply_markup=ForceReply())
        
        await message.answer("✅ Xabaringiz adminlarga yuborildi. Javobni kuting.")
    
    except Exception as e:
        logger.error(f"Xabar yuborishda xato: {e}")
        await message.answer("❌ Xabar yuborishda xatolik yuz berdi. Iltimos, keyinroq urunib ko'ring.")

@dp.message(F.reply_to_message, F.from_user.id.in_(Config.ADMIN_IDS))
async def admin_to_user(message: Message):
    try:
        original_msg = message.reply_to_message.text or message.reply_to_message.caption
        
        if original_msg and "👤 Foydalanuvchi:" in original_msg:
            user_id_line = next(line for line in original_msg.split('\n') if "🆔 ID:" in line)
            user_id = int(user_id_line.split(":")[1].strip())
            
            reply_text = (
                "📩 Admin javobi:\n\n"
                f"{message.text}\n\n"
                "💬 Savolingiz bo'lsa, yana yozishingiz mumkin."
            )
            await bot.send_message(user_id, reply_text)
            await message.answer("✅ Javob foydalanuvchiga yuborildi.")
    
    except Exception as e:
        logger.error(f"Javob yuborishda xato: {e}")
        await message.answer("❌ Javob yuborishda xatolik. Foydalanuvchi ID topilmadi.")

@dp.message(F.text == "📊 Statistika")
async def show_statistics(message: types.Message):
    if message.from_user.id not in Config.ADMIN_IDS:
        await message.answer("❌ Siz admin emassiz!")
        return

    total_users = len(user_data)
    total_movies = len(movies_db)
    
    await message.answer(
        f"📊 Bot statistikasi:\n\n"
        f"👤 Foydalanuvchilar soni: {total_users}\n"
        f"🎬 Kinolar soni: {total_movies}"
    )




@dp.message(F.text == "📢 Reklama yuborish")
async def ask_for_advertisement(message: Message, state: FSMContext):
    """Admin uchun reklama yuborishni boshlash"""
    if message.from_user.id not in Config.ADMIN_IDS:
        await message.answer("❌ Sizda bunday huquq yo'q!")
        return
    
    await message.answer(
        "📢 Reklama yuborish uchun quyidagilardan birini yuboring:\n\n"
        "• Matn xabar\n"
        "• Rasm (sarlavha bilan)\n"
        "• Video (sarlavha bilan)\n"
        "• Dokument (sarlavha bilan)\n\n"
        "❗ Diqqat: Xabar barcha foydalanuvchilarga yuboriladi",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🔙 Bekor qilish")]],
            resize_keyboard=True
        )
    )
    await state.set_state("waiting_for_ad_content")

@dp.message(F.from_user.id.in_(Config.ADMIN_IDS), F.text == "🔙 Bekor qilish")
async def cancel_advertisement(message: Message, state: FSMContext):
    """Reklama yuborishni bekor qilish"""
    await state.clear()
    await message.answer(
        "❌ Reklama yuborish bekor qilindi.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🏠 Bosh menyu")]],
            resize_keyboard=True
        )
    )

@dp.message(F.from_user.id.in_(Config.ADMIN_IDS), StateFilter("waiting_for_ad_content"))
async def send_advertisement(message: Message, state: FSMContext):
    """Reklamani barcha foydalanuvchilarga yuborish"""
    if not user_data:
        await message.answer("⚠️ Hozircha hech qanday foydalanuvchi yo'q!")
        await state.clear()
        return

    total_users = len(user_data)
    success = 0
    failed = 0
    
    # Progress xabarini yuborish
    progress_msg = await message.answer(f"⏳ Reklama yuborilmoqda... 0/{total_users}")
    
    try:
        for index, user_id in enumerate(user_data, 1):
            try:
                if message.text:
                    await bot.send_message(
                        chat_id=user_id,
                        text=message.text,
                        disable_web_page_preview=True
                    )
                elif message.photo:
                    await bot.send_photo(
                        chat_id=user_id,
                        photo=message.photo[-1].file_id,
                        caption=message.caption
                    )
                elif message.video:
                    await bot.send_video(
                        chat_id=user_id,
                        video=message.video.file_id,
                        caption=message.caption
                    )
                elif message.document:
                    await bot.send_document(
                        chat_id=user_id,
                        document=message.document.file_id,
                        caption=message.caption
                    )
                success += 1
                
                # Har 10 yoki oxirgi foydalanuvchi uchun progress yangilash
                if index % 10 == 0 or index == total_users:
                    try:
                        await progress_msg.edit_text(
                            f"⏳ Reklama yuborilmoqda... {index}/{total_users}\n"
                            f"✅ Muvaffaqiyatli: {success}\n"
                            f"❌ Xatolar: {failed}"
                        )
                    except Exception as e:
                        logger.error(f"Progress yangilashda xato: {e}")
                        
            except exceptions.TelegramForbiddenError:
                failed += 1  # Foydalanuvchi botni bloklagan
            except exceptions.TelegramBadRequest as e:
                logger.error(f"Xato (User ID: {user_id}): {e}")
                failed += 1
            except Exception as e:
                logger.error(f"Kutilmagan xato (User ID: {user_id}): {e}")
                failed += 1
                
        # Yakuniy natija
        await message.answer(
            f"📊 Reklama yuborish yakunlandi!\n\n"
            f"👤 Jami foydalanuvchilar: {total_users}\n"
            f"✅ Muvaffaqiyatli yuborildi: {success}\n"
            f"❌ Yuborilmadi: {failed}\n\n"
            f"📈 Muvaffaqiyat darajasi: {round(success/total_users*100, 2)}%"
        )
        
    finally:
        await state.clear()
        try:
            await progress_msg.delete()
        except:
            pass





@dp.message(F.text == "🏠 Asosiy menyu")
async def back_to_main_menu(message: types.Message):
    await start_cmd(message)

async def main():
    logger.info("Bot ishga tushmoqda...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
