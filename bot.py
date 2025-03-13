from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, PollAnswerHandler, CallbackQueryHandler

TOKEN = "7267797063:AAHjnlqhlLYU1rEAXf2S1VWLbKrTICagnak"

# 📌 1-bo‘lim test savollari
quiz1_questions = [
 {
        "question": "'Yo‘q bo‘lmoq' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["Absent from", "Accompanied by", "Account for", "Accuse smb of"],
        "correct_option_id": 0
    },
    {
        "question": "'Bilan hamroh' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["Amazed at/by", "Accompanied by", "Angry at what smb does", "Ashamed of"],
        "correct_option_id": 1
    },
    {
        "question": "'...ga muvofiq' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["According to", "Advantage of", "Astonished at/by", "Apply to smb for smth"],
        "correct_option_id": 0
    },
    {
        "question": "'Hisobga olmoq' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["Accused of", "Account for", "Advantage of", "Agree to"],
        "correct_option_id": 1
    },
    {
        "question": "'Ayblamoq' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["Accuse smb of", "Accustomed to", "Addicted to", "Apologize to smb for smth"],
        "correct_option_id": 0
    },
    {
        "question": "'Odatlangan' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["Afraid of", "Amazed at/by", "Accustomed to", "Angry with smb about smth"],
        "correct_option_id": 2
    },
    {
        "question": "'Berilib ketgan' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["Addicted to", "Approve of", "Argue with smb about smth", "Ask for"],
        "correct_option_id": 0
    },
    {
        "question": "'Ustunlik, afzallik' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["Advice on", "Advantage of", "Angry with smb for doing smth", "Arrive in"],
        "correct_option_id": 1
    },
    {
        "question": "'Maslahat' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["Agree on smth", "Advice on", "Aim at", "Amused at/with"],
        "correct_option_id": 1
    },
    {
        "question": "'Ko‘nmoq, rozi bo‘lmoq' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["Agree to", "Appeal to/against", "Attach to", "Afraid of"],
        "correct_option_id": 0
    },
    {
        "question": "'Kelishmoq' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["Agree on smth", "Astonished at/by", "Assure smb of", "Apologize to smb for smth"],
        "correct_option_id": 0
    },
    {
        "question": "'Hamfikr bo‘lish, rozi bo‘lish' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["Apply to smb for smth", "Argue with smb about smth", "Agree with smb", "Aim at"],
        "correct_option_id": 2
    },
    {
        "question": "'Oldida' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["Afraid of", "Astonished at/by", "Ahead of", "Amused at/with"],
        "correct_option_id": 2
    },
    {
        "question": "'Maqsad' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["Apologize to smb for smth", "Aim at", "Angry at what smb does", "Arrest smb for smth"],
        "correct_option_id": 1
    },
    {
        "question": "'Allergiyali' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["Allergic to", "Annoyed with smb about smth", "Afraid of", "Ashamed of"],
        "correct_option_id": 0
    },
    {
        "question": "'Hayratda qolgan' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["Amused at/with", "Amazed at/by", "Apologize to smb for smth", "Ask for"],
        "correct_option_id": 1
    },
    {
        "question": "'Xursand' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["Amused at/with", "Argue with smb about smth", "Arrive in", "Arrest smb for smth"],
        "correct_option_id": 0
    },
    {
        "question": "'Jahl chiqmoq' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["Angry with smb about smth", "Apologize to smb for smth", "Attach to", "Ahead of"],
        "correct_option_id": 0
    },
    {
        "question": "'Qo‘rqqan' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["Afraid of", "Astonished at/by", "Annoyed with smb about smth", "Appeal to/against"],
        "correct_option_id": 0
    },
    {
        "question": "'Achchiqlanmoq' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["Amazed at/by", "Annoyed with smb about smth", "Advantage of", "Agree to"],
        "correct_option_id": 1
    },
    {
        "question": "'Javob' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["(in) answer to", "Apologize to smb for smth", "Afraid of", "Appeal to/against"],
        "correct_option_id": 0
    },
    {
        "question": "'Xavotirlanmoq, tashvishlanmoq' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["Anxious about smth", "Astonished at/by", "Arrive at", "Apologize to smb for smth"],
        "correct_option_id": 0
    },
    {
        "question": "'Kechirim so‘ramoq' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["Apologize to smb for smth", "Angry at what smb does", "Assure smb of", "Ask for"],
        "correct_option_id": 0
    },
    {
        "question": "'Hibsga olmoq' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["Arrive in", "Arrest smb for smth", "Attach to", "Appeal to/against"],
        "correct_option_id": 1
    }
]

# 📌 2-bo‘lim test savollari
quiz2_questions = [
   {
        "question": "'Ko‘rmoq/tushunmoq' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["SEE", "FEEL", "LOOK", "NOTICE"],
        "correct_option_id": 2
    },
    {
        "question": "'Rohatlanmoq' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["LIKE", "ENJOY", "PREFER", "LOVE"],
        "correct_option_id": 3
    },
    {
        "question": "'His qilmoq' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["NOTICE", "FEEL", "HAVE", "MEASURE"],
        "correct_option_id": 1
    },
    {
        "question": "'Yoqtirmoq' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["LIKE", "HATE", "LOVE", "BELIEVE"],
        "correct_option_id": 0
    },
    {
        "question": "'Yoqtirmaslik' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["DISLIKE", "DETEST", "HATE", "REFUSE"],
        "correct_option_id": 1
    },
    {
        "question": "'O‘z ichiga olmoq' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["CONTAIN", "INCLUDE", "MEAN", "SUPPOSE"],
        "correct_option_id": 2
    },
    {
        "question": "'Ahamiyat kasb etmoq' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["MATTER", "MEASURE", "COST", "OWE"],
        "correct_option_id": 3
    },
    {
        "question": "'Muhtoj bo‘lmoq' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["WISH", "EXPECT", "REQUIRE", "DESIRE"],
        "correct_option_id": 2
    },
    {
        "question": "'Xohlamoq/tilak bildirmoq' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["WISH", "HOPE", "WANT", "DESIRE"],
        "correct_option_id": 3
    },
    {
        "question": "'Sevmoq' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["LOVE", "LIKE", "APPRECIATE", "ADORE"],
        "correct_option_id": 2
    },
    {
        "question": "'Nafratlanmoq' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["HATE", "DISLIKE", "DETEST", "DENY"],
        "correct_option_id": 3
    },
    {
        "question": "'Tuyulmoq (tashqi ko‘rinish)' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["SEEM", "APPEAR", "LOOK LIKE", "SOUND"],
        "correct_option_id": 2
    },
    {
        "question": "'Tuyulmoq (holat)' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["SEEM", "LOOK", "THINK", "NOTICE"],
        "correct_option_id": 3
    },
    {
        "question": "'Ishonmoq' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["BELIEVE", "SUPPOSE", "KNOW", "UNDERSTAND"],
        "correct_option_id": 1
    },
    {
        "question": "'Tegishli bo‘lmoq' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["BELONG", "OWN", "HAVE", "EQUAL"],
        "correct_option_id": 3
    },
    {
        "question": "'Unutmoq' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["FORGET", "REMEMBER", "RECOGNISE", "NOTICE"],
        "correct_option_id": 2
    },
    {
        "question": "'Eshitmoq' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["LISTEN", "HEAR", "NOTICE", "SOUND"],
        "correct_option_id": 3
    },
    {
        "question": "'Bilmoq' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["KNOW", "THINK", "BELIEVE", "SUPPOSE"],
        "correct_option_id": 1
    },
    {
        "question": "'Vaznga ega bo‘lmoq' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["WEIGH", "MEASURE", "FIT", "OWN"],
        "correct_option_id": 2
    },
    {
        "question": "'Kutmoq' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["WAIT", "EXPECT", "HOPE", "SUPPOSE"],
        "correct_option_id": 0
    },
    {
        "question": "'Hasad/rashk qilmoq' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["ENVY", "HATE", "DETEST", "DISLIKE"],
        "correct_option_id": 2
    },
    {
        "question": "'O‘xshamoq' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["LOOK LIKE", "RESEMBLE", "APPEAR", "SEEM"],
        "correct_option_id": 0
    },
    {
        "question": "'Rad qilmoq' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["REFUSE", "DENY", "SUPPOSE", "DISLIKE"],
        "correct_option_id": 2
    },
    {
        "question": "'Kechirmoq' so‘zining inglizcha ekvivalenti qaysi?",
        "options": ["FORGIVE", "REGRET", "ACCEPT", "APPRECIATE"],
        "correct_option_id": 2
    }
]

# 📌 Foydalanuvchining testdagi holatini saqlash
user_quiz_progress = {}

# 📌 /start buyrug‘iga javob
def start_command(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id, "Salom! 😊 Testni boshlash uchun /quiz1 yoki /quiz2 buyrug‘ini yuboring.")

# 📌 Testni boshlash funksiyasi
def start_quiz(update: Update, context: CallbackContext, quiz_questions, quiz_type: str) -> None:
    chat_id = update.message.chat_id
    user_quiz_progress[chat_id] = {"index": 0, "correct": 0, "quiz_type": quiz_type, "questions": quiz_questions}
    send_quiz(update, context, chat_id)

# 📌 Testni chiqarish funksiyasi
def send_quiz(update: Update, context: CallbackContext, chat_id: int) -> None:
    user_data = user_quiz_progress.get(chat_id, None)
    if not user_data:
        return

    index = user_data["index"]
    quiz_questions = user_data["questions"]

    # Agar barcha testlar tugagan bo‘lsa
    if index >= len(quiz_questions):
        correct_answers = user_data["correct"]
        total_questions = len(quiz_questions)
        score_text = f"✅ Test tugadi! Siz {total_questions} ta savoldan {correct_answers} tasiga to‘g‘ri javob berdingiz."
        
        keyboard = [[InlineKeyboardButton("🔄 Qayta yechish", callback_data=f"restart_{user_data['quiz_type']}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        context.bot.send_message(chat_id, score_text, reply_markup=reply_markup)
        return

    question_data = quiz_questions[index]

    # So‘rovnomani yuborish
    context.bot.send_poll(
        chat_id=chat_id,
        question=question_data["question"],
        options=question_data["options"],
        type="quiz",
        correct_option_id=question_data["correct_option_id"],
        is_anonymous=False
    )

# 📌 Foydalanuvchi javob bersa, natijani saqlash va keyingi savolni jo‘natish
def handle_poll_answer(update: Update, context: CallbackContext) -> None:
    poll_answer = update.poll_answer
    user_id = poll_answer.user.id  # Foydalanuvchi ID
    user_data = user_quiz_progress.get(user_id, None)

    if not user_data:
        return

    index = user_data["index"]
    quiz_questions = user_data["questions"]

    if index >= len(quiz_questions):
        return  # Agar test tugagan bo‘lsa, hech narsa qilmaymiz

    question_data = quiz_questions[index]

    # Foydalanuvchi to‘g‘ri javob berganini tekshiramiz
    if poll_answer.option_ids and poll_answer.option_ids[0] == question_data["correct_option_id"]:
        user_data["correct"] += 1  # To‘g‘ri javoblar sonini oshiramiz

    user_data["index"] += 1  # Keyingi savolga o'tish

    # Keyingi savolni yuborish
    send_quiz(update, context, user_id)

# 📌 "Next" tugmasini bosganda keyingi testga o‘tish (agar kerak bo‘lsa)
def next_question(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.message.chat_id
    send_quiz(update, context, chat_id)

# 📌 Testni qayta boshlash
def restart_quiz(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.message.chat_id
    quiz_type = query.data.split("_")[1]

    if quiz_type == "quiz1":
        start_quiz(update, context, quiz1_questions, "quiz1")
    elif quiz_type == "quiz2":
        start_quiz(update, context, quiz2_questions, "quiz2")

# 📌 Botni ishga tushirish
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("quiz1", lambda u, c: start_quiz(u, c, quiz1_questions, "quiz1")))
    dp.add_handler(CommandHandler("quiz2", lambda u, c: start_quiz(u, c, quiz2_questions, "quiz2")))
    dp.add_handler(PollAnswerHandler(handle_poll_answer))
    dp.add_handler(CallbackQueryHandler(next_question, pattern="next_question"))
    dp.add_handler(CallbackQueryHandler(restart_quiz, pattern="restart_.*"))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
