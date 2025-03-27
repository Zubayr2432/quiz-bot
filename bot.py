import sqlite3
import logging
from datetime import datetime
import asyncio
from aiogram import Bot, Dispatcher, types, F, Router 
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message, ForceReply
from aiogram.enums import ParseMode

# Enhanced configuration with type hints and better organization
class Config:
    CHANNEL_USERNAME = "ajoyib_kino_kodlari1"
    CHANNEL_LINK = f"https://t.me/{CHANNEL_USERNAME}"
    CHANNEL_ID = -1002341118048
    CHANNEL_USERNAME_sh = "+ZRxWtd33UQc5YzQy"  # Hidden channel
    CHANNEL_LINK_sh = f"https://t.me/{CHANNEL_USERNAME_sh}"
    CHANNEL_ID_sh = -1002537276349
    BOT_TOKEN = "7808158374:AAGMY8mkb0HVi--N2aJyRrPxrjotI6rnm7k"
    ADMIN_IDS = [7871012050, 7183540853]  # Admins list
    BATCH_SIZE = 30  # For bulk operations
    BATCH_DELAY = 1  # Delay between batches in seconds

# Improved logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize bot with better error handling
try:
    bot = Bot(token=Config.BOT_TOKEN, parse_mode=ParseMode.HTML)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    router = Router()
except Exception as e:
    logger.critical(f"Failed to initialize bot: {e}")
    raise

# Database class with connection pooling and better error handling
class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            try:
                cls._instance.conn = sqlite3.connect(
                    'kino.db',
                    check_same_thread=False,
                    timeout=30,
                    isolation_level=None
                )
                cls._instance.conn.row_factory = sqlite3.Row
                cls._instance.create_tables()
                logger.info("Database connection established")
            except sqlite3.Error as e:
                logger.error(f"Database connection failed: {e}")
                raise
        return cls._instance

    def create_tables(self):
        """Create database tables with better schema"""
        tables = [
            '''CREATE TABLE IF NOT EXISTS kinolar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kod INTEGER UNIQUE,
                nomi TEXT,
                file_id TEXT,
                kanal_msg_id INTEGER,
                sana TEXT DEFAULT CURRENT_TIMESTAMP,
                views INTEGER DEFAULT 0)''',
                
            '''CREATE TABLE IF NOT EXISTS adminlar (
                user_id INTEGER PRIMARY KEY,
                ism TEXT,
                added_at TEXT DEFAULT CURRENT_TIMESTAMP)''',
                
            '''CREATE TABLE IF NOT EXISTS foydalanuvchilar (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                joined_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_active TEXT)''',
                
            '''CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                admin_id INTEGER,
                message_text TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES foydalanuvchilar(user_id))'''
        ]
        
        try:
            with self.conn:
                for table in tables:
                    self.conn.execute(table)
                
                # Add default admin if not exists
                for admin_id in Config.ADMIN_IDS:
                    self.conn.execute(
                        "INSERT OR IGNORE INTO adminlar (user_id, ism) VALUES (?, ?)", 
                        (admin_id, "Admin")
                    )
                self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Database table creation error: {e}")
            raise

    def add_user(self, user: types.User):
        """Add user with complete info"""
        try:
            self.execute(
                """INSERT OR IGNORE INTO foydalanuvchilar 
                (user_id, username, full_name, last_active) 
                VALUES (?, ?, ?, datetime('now'))""",
                (user.id, user.username, user.full_name),
                commit=True
            )
            # Update last active time
            self.execute(
                "UPDATE foydalanuvchilar SET last_active = datetime('now') WHERE user_id = ?",
                (user.id,),
                commit=True
            )
            return True
        except sqlite3.Error as e:
            logger.error(f"Add user error: {e}")
            return False

    def execute(self, query, params=(), fetchone=False, fetchall=False, commit=False):
        """Improved execute with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                cur = self.conn.cursor()
                cur.execute(query, params)
                if commit:
                    self.conn.commit()
                if fetchone:
                    return cur.fetchone()
                if fetchall:
                    return cur.fetchall()
                return None
            except sqlite3.OperationalError as e:
                if "locked" in str(e) and attempt < max_retries - 1:
                    logger.warning(f"Database locked, retrying... (attempt {attempt + 1})")
                    time.sleep(0.5)
                    continue
                logger.error(f"SQL Error: {e}")
                return None
            except sqlite3.Error as e:
                logger.error(f"SQL Error: {e}")
                return None

    def close(self):
        """Close connection properly"""
        try:
            if self.conn:
                self.conn.close()
                logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database: {e}")

# States with better organization
class AdminState(StatesGroup):
    kino_nomi = State()
    kino_qoshish = State()
    kino_ochirish = State()
    reklama = State()
    contact_admin = State()
    add_admin = State()
    remove_admin = State()

# Helper functions with better error handling
async def check_subscription(user_id: int) -> bool:
    """Check if user is subscribed to channel with retry logic"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            member = await bot.get_chat_member(chat_id=Config.CHANNEL_ID, user_id=user_id)
            return member.status in ['member', 'administrator', 'creator']
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Subscription check failed: {e}")
                return False
            await asyncio.sleep(1)

async def ask_for_subscription(message: types.Message):
    """Improved subscription request with better keyboard"""
    builder = InlineKeyboardBuilder()
    builder.button(text="📢 Kanalga o'tish", url=Config.CHANNEL_LINK)
    builder.button(text="✅ Obuna bo'ldim", callback_data="check_subscription")
    builder.adjust(1)

    await message.answer(
        "🤖 Botdan to'liq foydalanish uchun quyidagi kanalga obuna bo'ling:\n"
        f"{Config.CHANNEL_LINK}\n\n"
        "Obuna bo'lgach, <b>'✅ Obuna bo'ldim'</b> tugmasini bosing.",
        reply_markup=builder.as_markup(),
        disable_web_page_preview=True
    )

async def is_admin(user_id: int) -> bool:
    """Check if user is admin with caching"""
    return user_id in Config.ADMIN_IDS

async def save_to_database(content_type: str, content_data: dict, code: int = None) -> bool:
    """Generic content saving to database"""
    db = Database()
    try:
        if content_type == "movie":
            db.execute(
                """INSERT INTO kinolar (kod, nomi, file_id) 
                VALUES (?, ?, ?)""",
                (code, content_data['nomi'], content_data['file_id']),
                commit=True
            )
            return True
        # Add other content types as needed
    except Exception as e:
        logger.error(f"Save to DB failed: {e}")
        return False

# ========================
# HANDLERS IMPROVEMENTS
# ========================

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    """Enhanced start command with user tracking"""
    user = message.from_user
    db = Database()
    
    # Save/update user info
    db.add_user(user)
    
    # Check subscription
    if not await check_subscription(user.id):
        await ask_for_subscription(message)
        return
    
    # Welcome message with better formatting
    welcome_msg = (
        "🎉 <b>Botdan foydalanishga xush kelibsiz!</b>\n\n"
        "Quyidagi menyudan kerakli bo'limni tanlang yoki kino kodini yuboring.\n\n"
        f"🔍 Kino izlash uchun kodni yuboring\n"
        f"📞 Savol uchun 'Adminga murojaat' tugmasini bosing\n\n"
        f"📢 Bizning kanal: {Config.CHANNEL_LINK}"
    )
    
    builder = ReplyKeyboardBuilder()
    builder.button(text="📞 Adminga murojaat")
    builder.adjust(2)
    
    await message.answer(welcome_msg, reply_markup=builder.as_markup(resize_keyboard=True))

@dp.callback_query(F.data == "check_subscription")
async def verify_subscription(query: types.CallbackQuery):
    """Subscription verification with better flow"""
    user = query.from_user
    
    if await check_subscription(user.id):
        try:
            await query.message.delete()
        except Exception as e:
            logger.warning(f"Message delete failed: {e}")
        
        await query.answer("✅ Obuna tasdiqlandi!", show_alert=True)
        await start_cmd(query.message)
    else:
        await query.answer("❌ Obuna tasdiqlanmadi!", show_alert=True)
        await ask_for_subscription(query.message)

# Admin panel with more features
@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    """Enhanced admin panel with more options"""
    if not await is_admin(message.from_user.id):
        await message.answer("⛔ Ruxsat yo'q!")
        return
    
    admin_menu = (
        "👨‍💻 <b>Admin panel</b>\n\n"
        "Quyidagi amallardan birini tanlang:"
    )
    
    builder = ReplyKeyboardBuilder()
    builder.button(text="🎬 Kino qo'shish")
    builder.button(text="🗑 Kino o'chirish")
    builder.button(text="📊 Statistika")
    builder.button(text="📢 Reklama yuborish")
    builder.button(text="⬅️ Asosiy menyu")
    builder.adjust(2, 2, 2)
    
    await message.answer(admin_menu, reply_markup=builder.as_markup(resize_keyboard=True))

# Movie addition with better flow
@dp.message(F.text == "🎬 Kino qo'shish")
async def start_add_movie(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    
    await message.answer(
        "🎥 <b>Yangi kino qo'shish</b>\n\n"
        "Kino nomini yuboring:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="◀️ Ortga")]],
            resize_keyboard=True
        )
    )
    await state.set_state(AdminState.kino_nomi)

@dp.message(AdminState.kino_nomi)
async def process_movie_name(message: types.Message, state: FSMContext):
    if message.text == "◀️ Ortga":
        await state.clear()
        await admin_panel(message)
        return
    
    await state.update_data(nomi=message.text)
    await message.answer(
        "📹 Endi kino videosini yuboring:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="◀️ Ortga")]],
            resize_keyboard=True
        )
    )
    await state.set_state(AdminState.kino_qoshish)

@dp.message(AdminState.kino_qoshish)
async def process_movie(message: types.Message, state: FSMContext):
    if message.text == "◀️ Ortga":
        await state.clear()
        await admin_panel(message)
        return

    if not message.video:
        await message.answer("❌ Faqat video qabul qilinadi!")
        return
    
    data = await state.get_data()
    nomi = data.get("nomi", "Nomsiz")
    
    # Generate new code
    db = Database()
    new_code = db.execute("SELECT MAX(kod) FROM kinolar", fetchone=True)[0] or 1000
    new_code += 1
    
    # Save to channel and database
    try:
        # Post to main channel
        bot_username = (await bot.get_me()).username
        caption = (
            f"🎬 <b>{nomi}</b>\n\n"
            f"🔢 Kodi: <code>{new_code}</code>\n\n"
            f"📥 @{bot_username} orqali yuklab olish mumkin\n"
            f"🔗 Kanal: {Config.CHANNEL_LINK}"
        )
        
        msg = await bot.send_message(
            chat_id=Config.CHANNEL_ID_sh,
            text=caption
        )
        
        await bot.send_video(
            chat_id=Config.CHANNEL_ID_sh,
            video=message.video.file_id,
            reply_to_message_id=msg.message_id,
            caption=caption
        )
        
        # Save to database
        db.execute(
            "INSERT INTO kinolar (kod, nomi, file_id, kanal_msg_id) VALUES (?, ?, ?, ?)",
            (new_code, nomi, message.video.file_id, msg.message_id),
            commit=True
        )
        
        # Success message
        success_msg = (
            f"✅ <b>Kino muvaffaqiyatli qo'shildi!</b>\n\n"
            f"📝 Nomi: {nomi}\n"
            f"🔢 Kodi: <code>{new_code}</code>\n"
            f"🔗 <a href='https://t.me/{Config.CHANNEL_USERNAME}/{msg.message_id}'>Kanaldagi post</a>"
        )
        await message.answer(success_msg)
        
    except Exception as e:
        logger.error(f"Movie addition failed: {e}")
        await message.answer(f"❌ Xatolik: {str(e)}")
    
    await state.clear()

@dp.message(F.text == "🗑 Kino o'chirish")
async def start_delete_movie(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    
    await message.answer("O'chirmoqchi bo'lgan kino kodini yuboring:")
    await state.set_state(AdminState.kino_ochirish)

@dp.message(AdminState.kino_ochirish)
async def process_delete_movie(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Iltimos, faqat raqam yuboring!")
        return
    
    kod = int(message.text)
    db = Database()
    
    try:
        result = db.execute("SELECT kanal_msg_id FROM kinolar WHERE kod=?", (kod,), fetchone=True)
        
        if result:
            try:
                await bot.delete_message(chat_id=f"@{Config.CHANNEL_USERNAME}", message_id=result["kanal_msg_id"])
            except Exception as e:
                logger.warning(f"Error deleting channel message: {e}")
            
            db.execute("DELETE FROM kinolar WHERE kod=?", (kod,), commit=True)
            await message.answer(f"✅ {kod}-kodli kino muvaffaqiyatli o'chirildi!")
        else:
            await message.answer("❌ Bunday kodli kino topilmadi!")
    
    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")
    
    finally:
        await state.clear()

# Statistics with more details
@dp.message(F.text == "📊 Statistika")
async def show_stats(message: types.Message):
    if not await is_admin(message.from_user.id):
        return
    
    db = Database()
    
    try:
        # Get movie stats
        movie_stats = db.execute(
            "SELECT COUNT(*) as count, MIN(sana) as first_date, MAX(sana) as last_date FROM kinolar",
            fetchone=True
        )
        
        # Get user stats
        user_stats = db.execute(
            "SELECT COUNT(*) as total, "
            "SUM(CASE WHEN last_active > datetime('now', '-1 day') THEN 1 ELSE 0 END) as active_today "
            "FROM foydalanuvchilar",
            fetchone=True
        )
        
        # Format stats message
        stats_msg = (
            "📊 <b>Bot statistikasi</b>\n\n"
            "🎬 <b>Kinolar:</b>\n"
            f"• Jami: {movie_stats['count']}\n"
            f"• Birinchi: {movie_stats['first_date'] or 'N/A'}\n"
            f"• Oxirgi: {movie_stats['last_date'] or 'N/A'}\n\n"
            "👥 <b>Foydalanuvchilar:</b>\n"
            f"• Jami: {user_stats['total']}\n"
            f"• Faol (24 soat): {user_stats['active_today']}\n\n"
            f"🔗 Kanal: {Config.CHANNEL_LINK}"
        )
        
        await message.answer(stats_msg)
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        await message.answer("❌ Statistika olishda xatolik")

# Enhanced advertisement sending
@dp.message(F.text == "📢 Reklama yuborish")
async def start_advertisement(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    
    await message.answer(
        "✍️ Reklama matnini yuboring yoki media (rasm, video, fayl) jo'nating:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="◀️ Ortga")]],
            resize_keyboard=True
        )
    )
    await state.set_state(AdminState.reklama)

@dp.message(AdminState.reklama)
async def send_advertisement(message: types.Message, state: FSMContext):
    if message.text == "◀️ Ortga":
        await state.clear()
        await admin_panel(message)
        return
    
    # Prepare content
    content = {
        'type': message.content_type,
        'text': message.text or message.caption or "",
        'file_id': getattr(message, message.content_type).file_id if message.content_type != 'text' else None
    }
    
    # Get all users
    db = Database()
    users = [row['user_id'] for row in db.execute("SELECT user_id FROM foydalanuvchilar", fetchall=True)]
    
    if not users:
        await message.answer("⚠️ Hozircha foydalanuvchilar yo'q!")
        return
    
    # Send with progress
    total = len(users)
    success = 0
    progress_msg = await message.answer(f"📤 Yuborilmoqda... 0/{total} (0%)")
    
    for i, user_id in enumerate(users, 1):
        try:
            if content['type'] == 'text':
                await bot.send_message(user_id, content['text'])
            else:
                method = getattr(bot, f"send_{content['type']}")
                await method(user_id, content['file_id'], caption=content['text'])
            success += 1
        except Exception as e:
            logger.warning(f"Failed to send to {user_id}: {e}")
        
        # Update progress every 10 users or last one
        if i % 10 == 0 or i == total:
            percent = int((i / total) * 100)
            await progress_msg.edit_text(
                f"📤 Yuborilmoqda... {i}/{total} ({percent}%)\n"
                f"✅ Muvaffaqiyatli: {success}\n"
                f"❌ Xatolar: {i - success}"
            )
            await asyncio.sleep(Config.BATCH_DELAY)
    
    # Final report
    await progress_msg.delete()
    await message.answer(
        f"✅ Reklama yuborish yakunlandi!\n\n"
        f"📊 Natijalar:\n"
        f"• Jami: {total}\n"
        f"• Muvaffaqiyatli: {success}\n"
        f"• Xatolar: {total - success}",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="⬅️ Asosiy menyu")]],
            resize_keyboard=True
        )
    )
    await state.clear()


# Movie search by code
@dp.message(lambda message: message.text.isdigit())
async def send_movie_by_code(message: types.Message):
    # Check subscription first
    if not await check_subscription(message.from_user.id):
        await ask_for_subscription(message)
        return
    
    code = int(message.text)
    db = Database()
    movie = db.execute("SELECT nomi, file_id FROM kinolar WHERE kod = ?", (code,), fetchone=True)
    
    if not movie:
        await message.answer(
            f"❌ {code}-kodli kino topilmadi!\n\n"
            f"🔍 Kanalda barcha kinolar: {Config.CHANNEL_LINK}",
            disable_web_page_preview=True
        )
        return
    
    # Send movie
    try:
        await message.answer_video(
            video=movie['file_id'],
            caption=f"🎬 <b>{movie['nomi']}</b>\n\n🔢 Kodi: <code>{code}</code>"
        )
        # Increment view count
        db.execute("UPDATE kinolar SET views = views + 1 WHERE kod = ?", (code,), commit=True)
    except Exception as e:
        logger.error(f"Movie send failed: {e}")
        await message.answer("❌ Kino yuborishda xatolik")

# Contact admin with better tracking
@dp.message(F.text == "📞 Adminga murojaat")
async def contact_admin(message: types.Message, state: FSMContext):
    await message.answer(
        "✍️ Xabaringizni yuboring (matn, rasm, video yoki fayl):\n\n"
        "Adminlar tez orada javob berishadi.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="◀️ Bekor qilish")]],
            resize_keyboard=True
        )
    )
    await state.set_state(AdminState.contact_admin)

@dp.message(AdminState.contact_admin)
async def forward_to_admin(message: types.Message, state: FSMContext):
    if message.text == "◀️ Bekor qilish":
        await state.clear()
        await start_cmd(message)
        return
    
    user = message.from_user
    user_info = (
        f"👤 <b>Foydalanuvchi:</b> {user.full_name}\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"📅 Sana: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    )
    
    try:
        if message.text:
            caption = f"{user_info}📝 Xabar: {message.text}"
            content = {'type': 'text', 'text': caption}
        elif message.photo:
            caption = f"{user_info}📷 Rasm"
            content = {'type': 'photo', 'file_id': message.photo[-1].file_id, 'caption': caption}
        elif message.video:
            caption = f"{user_info}🎥 Video"
            content = {'type': 'video', 'file_id': message.video.file_id, 'caption': caption}
        elif message.document:
            caption = f"{user_info}📄 Fayl: {message.document.file_name}"
            content = {'type': 'document', 'file_id': message.document.file_id, 'caption': caption}
        else:
            await message.answer("❌ Qabul qilinmaydigan format")
            return
        
        # Forward to all admins
        for admin_id in Config.ADMIN_IDS:
            try:
                if content['type'] == 'text':
                    await bot.send_message(
                        admin_id,
                        content['text'],
                        reply_markup=ForceReply()
                    )
                else:
                    method = getattr(bot, f"send_{content['type']}")
                    await method(
                        admin_id,
                        content['file_id'],
                        caption=content.get('caption'),
                        reply_markup=ForceReply()
                    )
            except Exception as e:
                logger.error(f"Failed to forward to admin {admin_id}: {e}")
        
        await message.answer(
            "✅ Xabaringiz adminlarga yuborildi. Javobni kuting.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="⬅️ Asosiy menyu")]],
                resize_keyboard=True
            )
        )
        await state.clear()
        
    except Exception as e:
        logger.error(f"Contact admin error: {e}")
        await message.answer("❌ Xabar yuborishda xatolik")

# Admin reply handler
@dp.message(F.reply_to_message, F.from_user.id.in_(Config.ADMIN_IDS))
async def handle_admin_reply(message: types.Message):
    try:
        original_msg = message.reply_to_message
        if not original_msg.text and not original_msg.caption:
            return
        
        text = original_msg.text or original_msg.caption
        if "👤 Foydalanuvchi:" not in text:
            return
        
        # Extract user ID
        lines = text.split('\n')
        user_id = None
        for line in lines:
            if "🆔 ID:" in line:
                user_id = int(line.split(":")[1].strip().replace('<code>', '').replace('</code>', ''))
                break
        
        if not user_id:
            await message.answer("❌ Foydalanuvchi ID topilmadi")
            return
        
        # Send reply
        reply_text = (
            "📩 <b>Admin javobi:</b>\n\n"
            f"{message.text}\n\n"
            "💬 Qo'shimcha savollar bo'lsa, yozishingiz mumkin."
        )
        
        try:
            await bot.send_message(user_id, reply_text)
            await message.answer("✅ Javob yuborildi!")
        except Exception as e:
            await message.answer(f"❌ Javob yuborish mumkin emas: {e}")
            
    except Exception as e:
        logger.error(f"Admin reply error: {e}")
        await message.answer("❌ Xatolik yuz berdi")

# ========================
# BOT MANAGEMENT
# ========================

async def on_startup():
    """Initialize database and other resources"""
    try:
        db = Database()
        logger.info("Bot ishga tushdi")
        
        # Send startup notification to admins
        for admin_id in Config.ADMIN_IDS:
            try:
                await bot.send_message(
                    admin_id,
                    "🤖 Bot ishga tushdi va tayyor!"
                )
            except Exception as e:
                logger.warning(f"Failed to notify admin {admin_id}: {e}")
    except Exception as e:
        logger.critical(f"Startup failed: {e}")
        raise

async def on_shutdown():
    """Cleanup resources"""
    try:
        db = Database()
        db.close()
        logger.info("Bot to'xtatildi")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

async def main():
    """Main bot function"""
    await on_startup()
    try:
        await dp.start_polling(bot)
    finally:
        await on_shutdown()

if __name__ == '__main__':
    asyncio.run(main())
