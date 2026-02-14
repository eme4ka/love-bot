import os
import telebot
from telebot import types
import time
import threading

# ===================== CONFIG =====================
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def p(name: str) -> str:
    """Absolute path helper (file next to bot.py)."""
    return os.path.join(BASE_DIR, name)

# ✅ ТВОЙ САЙТ (Netlify)
SITE_URL = "https://benevolent-choux-c33160.netlify.app"

# ===================== ADMIN PANEL =====================
ADMIN_ID = 966735372
ADMIN_LOG = True

def admin_log_text(text: str):
    if not ADMIN_LOG:
        return
    try:
        bot.send_message(ADMIN_ID, text)
    except:
        pass

def admin_forward(message):
    """Forward original user message to admin."""
    if not ADMIN_LOG:
        return
    try:
        bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    except:
        pass

# ===================== STORAGE =====================
user_state = {}
user_code = {}
photo_attempts = {}
truth_step = {}
photo_path_step = {}

# ====== Delete by blocks ======
block_msgs = {}  # {chat_id: {block_name: [message_id, ...]}}

def track(chat_id: int, block: str, msg_id: int):
    block_msgs.setdefault(chat_id, {}).setdefault(block, []).append(msg_id)

def track_user_msg(message, block: str):
    if message.chat.id != ADMIN_ID:
        track(message.chat.id, block, message.message_id)

def send_block(chat_id: int, text: str, block: str):
    msg = bot.send_message(chat_id, text)
    track(chat_id, block, msg.message_id)
    return msg

def send_voice_block(chat_id: int, path: str, caption: str, block: str):
    with open(path, "rb") as v:
        msg = bot.send_voice(chat_id, v, caption=caption)
    track(chat_id, block, msg.message_id)
    return msg

def send_photo_block(chat_id: int, path: str, caption: str, block: str):
    with open(path, "rb") as f:
        msg = bot.send_photo(chat_id, f, caption=caption)
    track(chat_id, block, msg.message_id)
    return msg

def send_video_block(chat_id: int, path: str, caption: str, block: str):
    """
    Try send_video, if fails (size/codec), send as document.
    """
    try:
        with open(path, "rb") as f:
            msg = bot.send_video(chat_id, f, caption=caption)
    except:
        with open(path, "rb") as f:
            msg = bot.send_document(chat_id, f, caption=caption)
    track(chat_id, block, msg.message_id)
    return msg

def delete_block(chat_id: int, block: str):
    ids = block_msgs.get(chat_id, {}).get(block, [])
    for mid in reversed(ids):
        try:
            bot.delete_message(chat_id, mid)
        except:
            pass
    if chat_id in block_msgs and block in block_msgs[chat_id]:
        block_msgs[chat_id][block] = []

# ===================== STATES =====================
CODE_1 = "code_1"
CODE_2 = "code_2"
CODE_3 = "code_3"
CODE_4 = "code_4"
CODE_5 = "code_5"
PHOTO_TRAP = "photo_trap"
WAIT_30 = "wait_30"
EMO_1 = "emo_1"
PASS_1 = "pass_1"

ROOM_1 = "room_1"
ROOM_2 = "room_2"
ROOM_3 = "room_3"
ROOM_4 = "room_4"
ROOM_5 = "room_5"

CIPHER = "cipher"
WAIT_60 = "wait_60"

TRUTH_1 = "truth_1"
TRUTH_2 = "truth_2"
TRUTH_3 = "truth_3"

PHOTO_PATH = "photo_path"
FINAL = "final"

# ===================== SETTINGS =====================
FINAL_CODE = "1287315"
SECRET_PASSWORD = "0712"
CIPHER_RESULT = "202920252023"

VOICE_PATH = p("love.ogg")

# ✅ MEDIA AFTER ANSWERS (NOT deleted)
IMG_CODE_1 = p("qwe.jpg")
IMG_CODE_2 = p("asd.jpg")
IMG_CODE_3 = p("zxc.jpg")
IMG_CODE_4 = p("rty.jpg")
VIDEO_CODE_5 = p("fgh.MP4")

# ✅ EXTRA MEDIA (NOT deleted)
PHOTO_AFTER_PHOTOTRAP = p("vbn.jpg")
VIDEO_DURING_WAIT30 = p("jkl.mp4")

# ✅ TIMER 60 SEC (video starts together with timer)
VIDEO_DURING_WAIT60 = p("plm.mp4")   # starts with timer
PHOTO_AFTER_WAIT60 = p("plm.jpg")    # after timer ends

# ✅ GAME 10 auto photos after each step
PHOTO_GAME10_1 = p("uhv.jpg")
PHOTO_GAME10_2 = p("dfv.jpg")
PHOTO_GAME10_3 = p("jvx.jpg")

# ===================== BLOCK NAMES =====================
B_INTRO = "intro"                 # /start /help /begin (deleted)
B_CODE = "code"                   # questions/answers 1-5 (deleted)
B_CODE_MEDIA = "code_media"       # photos/videos after answers (NOT deleted)

B_PHOTO = "photo_trap_text"       # photo-trap text/user msgs (deleted)
B_PHOTO_MEDIA = "photo_trap_media"  # vbn.jpg (NOT deleted)

B_WAIT30 = "wait30_text"          # wait 30 text (deleted)
B_WAIT30_MEDIA = "wait30_media"   # jkl.mp4 (NOT deleted)

B_EMO = "emo_text"                # her answer + prompt (deleted)
B_EMO_KEEP = "emo_keep"           # your message after her answer (NOT deleted)

B_PASS = "pass_text"              # password block (deleted)

B_ROOMS = "rooms_block"           # 5 rooms + voice (deleted)
B_CIPHER = "cipher_block"         # cipher block (deleted)

B_WAIT60 = "wait60_text"          # wait 60 text (deleted)
B_WAIT60_MEDIA = "wait60_media"   # plm.mp4 + plm.jpg (NOT deleted)

B_TRUTH = "truth_block"           # truth 1-3 (deleted)
B_PHOTOPATH = "photopath_block"   # her photos game10 (deleted)
B_PHOTOPATH_MEDIA = "photopath_media"  # auto-sent photos (NOT deleted)

B_FINAL = "final_block"           # final (NOT deleted)

# ===================== ADMIN COMMAND =====================
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.chat.id != ADMIN_ID:
        return

    lines = ["🛠 Адмін-панель", ""]
    if not user_state:
        lines.append("Немає активних користувачів зараз.")
    else:
        for cid, st in user_state.items():
            code = "".join(user_code.get(cid, []))
            attempts = photo_attempts.get(cid, 0)
            tstep = truth_step.get(cid, 0)
            pstep = photo_path_step.get(cid, 0)
            lines.append(
                f"• {cid}: state={st}\n"
                f"   code='{code}', photo_attempts={attempts}, truth_step={tstep}, photo_path_step={pstep}"
            )

    bot.send_message(message.chat.id, "\n".join(lines))

# ===================== START / HELP / BEGIN =====================
@bot.message_handler(commands=['start'])
def start_cmd(message):
    track_user_msg(message, B_INTRO)
    msg = bot.send_message(
        message.chat.id,
        "привіт моя кохана 🤍\n"
        "Я почав робити цього бота 7.02 спонтанно, але думав над кожним кроком.\n"
        "Я витрачав на нього по 5 годин на день, кожна година була витрачена з думкою як зробити щоб тобі сподобалось,\n"
        "це та сама причина чому я міг забувати відповісти😅\n"
        "Але ці всі слова це пустяк.\n Саме головне — що я тебе дуже кохаю 🫰\n\n"
        "Тисни /help 👆"
    )
    track(message.chat.id, B_INTRO, msg.message_id)

@bot.message_handler(commands=['help'])
def help_cmd(message):
    track_user_msg(message, B_INTRO)
    msg = bot.send_message(
        message.chat.id,
        "Це квест із багатьох частин який ти повинна пройти 🤍\n"
        "Кожна частинка поділенна, є моменти де ти повинна подумати, знайти та відправити😉\n"
        "Він буде довгий — але повністю звʼязаний з нами, тобі повинно сподобатись!!\n\n"
        "Тисни /begin 👆"
    )
    track(message.chat.id, B_INTRO, msg.message_id)

@bot.message_handler(commands=['begin'])
def begin_cmd(message):
    chat_id = message.chat.id

    admin_log_text(f"▶️ /begin від {message.from_user.first_name} ({chat_id})")
    admin_forward(message)

    track_user_msg(message, B_INTRO)

    user_state[chat_id] = CODE_1
    user_code[chat_id] = []
    photo_attempts[chat_id] = 0

    send_block(
        chat_id,
        "🧠 ГРА 1: КОД ПАМʼЯТІ\n\n"
        "Після кожної відповіді ти будеш отримувати приємне нагадування 📚\n\n"
        "Питання 1:\n"
        "В якому МІСЯЦІ ми вперше зустрілися?\n"
        "(напиши цифру)",
        B_CODE
    )

    delete_block(chat_id, B_INTRO)

# ===================== CODE 1-5 =====================
@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == CODE_1)
def code1(message):
    if not message.text.isdigit():
        return
    chat_id = message.chat.id

    admin_log_text(f"🔢 CODE_1 {chat_id}: {message.text}")
    admin_forward(message)

    track_user_msg(message, B_CODE)
    user_code[chat_id].append(message.text)

    try:
        send_photo_block(chat_id, IMG_CODE_1, "Це наша перша фотка разом, саме у цьому місяці 🤍", B_CODE_MEDIA)
    except:
        send_block(chat_id, "⚠️ Не знайшов qwe.jpg", B_CODE)

    user_state[chat_id] = CODE_2
    send_block(chat_id, "Питання 2:\nСкільки букв у слові «Квіточка»? 🌷", B_CODE)

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == CODE_2)
def code2(message):
    if not message.text.isdigit():
        return
    chat_id = message.chat.id

    admin_log_text(f"🔢 CODE_2 {chat_id}: {message.text}")
    admin_forward(message)

    track_user_msg(message, B_CODE)
    user_code[chat_id].append(message.text)

    try:
        send_photo_block(chat_id, IMG_CODE_2, "Приблизно стільки тобі було, коли тебе вперше назвали «квіточкою»? 🙈", B_CODE_MEDIA)
    except:
        send_block(chat_id, "⚠️ Не знайшов asd.jpg", B_CODE)

    user_state[chat_id] = CODE_3
    send_block(chat_id, "Питання 3:\nПерша цифра ДНЯ нашої зустрічі?🫂", B_CODE)

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == CODE_3)
def code3(message):
    if not message.text.isdigit():
        return
    chat_id = message.chat.id

    admin_log_text(f"🔢 CODE_3 {chat_id}: {message.text}")
    admin_forward(message)

    track_user_msg(message, B_CODE)
    user_code[chat_id].append(message.text)

    try:
        send_photo_block(chat_id, IMG_CODE_3, "А памʼятаєш, як ми хвилювались перед зустріччю? 🥹", B_CODE_MEDIA)
    except:
        send_block(chat_id, "⚠️ Не знайшов zxc.jpg", B_CODE)

    user_state[chat_id] = CODE_4
    send_block(chat_id, "Питання 4:\nА памʼятаєш, коли ми були на катку? ⛸️ (напиши цифру)", B_CODE)

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == CODE_4)
def code4(message):
    if not message.text.isdigit():
        return
    chat_id = message.chat.id

    admin_log_text(f"🔢 CODE_4 {chat_id}: {message.text}")
    admin_forward(message)

    track_user_msg(message, B_CODE)
    user_code[chat_id].append(message.text)

    try:
        send_photo_block(chat_id, IMG_CODE_4, "Це як ти змусила всіх зробити спільне фото 😋", B_CODE_MEDIA)
    except:
        send_block(chat_id, "⚠️ Не знайшов rty.jpg", B_CODE)

    user_state[chat_id] = CODE_5
    send_block(chat_id, "Питання 5:\nДень, коли ти мені вперше сказала «люблю» (напиши цифру)", B_CODE)

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == CODE_5)
def code5(message):
    if not message.text.isdigit():
        return
    chat_id = message.chat.id

    admin_log_text(f"🔢 CODE_5 {chat_id}: {message.text}")
    admin_forward(message)

    track_user_msg(message, B_CODE)
    user_code[chat_id].append(message.text)

    try:
        send_video_block(chat_id, VIDEO_CODE_5, "Саме після цього «люблю» і почались ці щасливі моменти 🤍", B_CODE_MEDIA)
    except:
        send_block(chat_id, "⚠️ Не знайшов fgh.MP4", B_CODE)

    code = "".join(user_code[chat_id])

    delete_block(chat_id, B_CODE)

    if code == FINAL_CODE:

        user_state[chat_id] = PHOTO_TRAP
        photo_attempts[chat_id] = 0
        send_block(
            chat_id,
            "📸 ГРА 2: ФОТО-ПАСТКА\n"
            "Надішли фото, де я щиро усміхаюсь.\n"
            "У тебе є 3 спроби",
            B_PHOTO
        )
    else:
        user_code[chat_id] = []
        user_state[chat_id] = CODE_1
        send_block(chat_id, "Код неправильний 😈\nПочнемо спочатку.\n\nПитання 1:", B_CODE)

# ===================== PHOTO HANDLER =====================
@bot.message_handler(content_types=['photo'])
def photo_handler(message):
    chat_id = message.chat.id
    st = user_state.get(chat_id)

    admin_log_text(f"📸 Фото від {message.from_user.first_name} ({chat_id}) | state={st}")
    admin_forward(message)

    if st == PHOTO_TRAP:
        track_user_msg(message, B_PHOTO)
        photo_attempts[chat_id] += 1

        if photo_attempts[chat_id] < 3:
            send_block(chat_id, f"Майже… 🤞\nСпроба {photo_attempts[chat_id]}/3", B_PHOTO)
        else:
            try:
                send_photo_block(chat_id, PHOTO_AFTER_PHOTOTRAP, "Оце та сама твоя посмішка 🥰", B_PHOTO_MEDIA)
            except:
                send_block(chat_id, "⚠️ Не знайшов vbn.jpg", B_PHOTO)

            delete_block(chat_id, B_PHOTO)

            user_state[chat_id] = WAIT_30

            try:
                send_video_block(chat_id, VIDEO_DURING_WAIT30, "Поки чекаєш… 🤍", B_WAIT30_MEDIA)
            except:
                send_block(chat_id, "⚠️ Не знайшов jkl.mp4", B_WAIT30)

            send_block(chat_id, "⏳ Наступний рівень через 30 секунд…", B_WAIT30)
            threading.Thread(target=wait_unlock_30, args=(chat_id,), daemon=True).start()
        return

    if st == PHOTO_PATH:
        track_user_msg(message, B_PHOTOPATH)
        photo_path_step[chat_id] += 1

        if photo_path_step[chat_id] == 1:
            try: send_photo_block(chat_id, PHOTO_GAME10_1, "памʼятаєш цей день як ми грали в ігри 😆", B_PHOTOPATH_MEDIA)
            except: pass
            send_block(chat_id, "📸 2/3\nТепер надішли фото, де МИ разом 🤍", B_PHOTOPATH)

        elif photo_path_step[chat_id] == 2:
            try: send_photo_block(chat_id, PHOTO_GAME10_2, "А це як ми назнімали у цей день кучу відео та фото 🥹", B_PHOTOPATH_MEDIA)
            except: pass
            send_block(chat_id, "📸 3/3\nНадішли фото, яке для тебе означає «МИ» (будь-яке)", B_PHOTOPATH)

        else:
            try: send_photo_block(chat_id, PHOTO_GAME10_3, "Саме стіч чомусь показує мені наші відносини, що може бути не все так легко, але разом 🫂", B_PHOTOPATH_MEDIA)
            except: pass

            delete_block(chat_id, B_PHOTOPATH)
            user_state[chat_id] = FINAL
            send_block(chat_id, "🎁 ФІНАЛ\nНапиши слово, яким ти хочеш закінчити цю історію.", B_FINAL)
        return

# ===================== WAIT 30 =====================
def wait_unlock_30(chat_id):
    time.sleep(30)
    delete_block(chat_id, B_WAIT30)

    user_state[chat_id] = EMO_1
    send_block(
        chat_id,
        "🧩 ГРА 3: ЧЕСНО\n"
        "Напиши, що ти відчула, коли ми вперше попрощались 🤍",
        B_EMO
    )

# ===================== GAME 3: EMO =====================
@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == EMO_1)
def emo1(message):
    chat_id = message.chat.id

    admin_log_text(f"💬 EMO_1 {chat_id}: {message.text}")
    admin_forward(message)

    track_user_msg(message, B_EMO)

    if len(message.text) < 20:
        send_block(chat_id, "Я знаю, що ти можеш сказати більше… 🤍", B_EMO)
        return

    send_block(
        chat_id,
        "Коли ми вперше прощалися з тобою, на душі була наче пустота. "
        "Я не знаю, як передати це словами, але від дня, коли ти поїхала, "
        "і до дня, коли я приїхав, минуло наче не місяць, а ціла вічність.",
        B_EMO_KEEP
    )

    delete_block(chat_id, B_EMO)

    user_state[chat_id] = PASS_1
    send_block(chat_id, "🔒 ГРА 4: ПАРОЛЬ\nВведи пароль.\n(найголовніша дата у наших відносинах)", B_PASS)

# ===================== PASSWORD =====================
@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == PASS_1)
def pass1(message):
    chat_id = message.chat.id

    admin_log_text(f"🔒 PASS_1 {chat_id}: {message.text}")
    admin_forward(message)

    track_user_msg(message, B_PASS)

    if message.text != SECRET_PASSWORD:
        send_block(chat_id, "Не той пароль 😈 Спробуй ще раз", B_PASS)
        return

    delete_block(chat_id, B_PASS)

    try:
        send_voice_block(chat_id, VOICE_PATH, "Прослухай 🤍", B_ROOMS)
    except:
        send_block(chat_id, "⚠️ Не знайшов love.ogg", B_ROOMS)

    user_state[chat_id] = ROOM_1
    send_block(chat_id,
        "✅ Правильно 🤍\n\n"
        "🏠 ГРА 5: КІМНАТИ СПОГАДІВ\n\n"
        "КІМНАТА 1:\nЯке було моє перше повідомлення тобі?",
        B_ROOMS
    )

# ===================== 5 ROOMS =====================
@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == ROOM_1)
def room1(message):
    chat_id = message.chat.id
    admin_forward(message)
    track_user_msg(message, B_ROOMS)
    user_state[chat_id] = ROOM_2
    send_block(chat_id, "КІМНАТА 2:\nДе була наша перша прогулянка?", B_ROOMS)

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == ROOM_2)
def room2(message):
    chat_id = message.chat.id
    admin_forward(message)
    track_user_msg(message, B_ROOMS)
    user_state[chat_id] = ROOM_3
    send_block(chat_id, "КІМНАТА 3:\nОпиши мене трьома словами 🤍", B_ROOMS)

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == ROOM_3)
def room3(message):
    chat_id = message.chat.id
    admin_forward(message)
    track_user_msg(message, B_ROOMS)
    send_block(chat_id, "Я тебе описую як:\n мила, гарна та щира дівчинка", B_CODE_MEDIA)
    user_state[chat_id] = ROOM_4
    send_block(chat_id, "КІМНАТА 4:\nПро що ти тоді подумала, але не сказала?", B_ROOMS)

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == ROOM_4)
def room4(message):
    chat_id = message.chat.id
    admin_forward(message)
    track_user_msg(message, B_ROOMS)
    send_block(
        chat_id,
        "Я в день знайомства завжди думав, як продовжити розмову, як підібрати слова, "
        "щоб утримати тебе у чаті. Шукав усі можливості, щоб з тобою поспілкуватися, кохана.",
        B_CODE_MEDIA
    )
    user_state[chat_id] = ROOM_5
    send_block(chat_id, "КІМНАТА 5:\nОдне слово, яке описує НАС", B_ROOMS)

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == ROOM_5)
def room5(message):
    chat_id = message.chat.id
    admin_forward(message)
    track_user_msg(message, B_ROOMS)
    send_block(chat_id, "Я важжаю що саме 'розуміння' у нас більш всього", B_CODE_MEDIA)

    delete_block(chat_id, B_ROOMS)

    user_state[chat_id] = CIPHER
    send_block(chat_id,
        "🔐 ГРА 6: ШИФР КОХАННЯ\n\n"
        "Слово: ЛЮБОВ\n"
        "А=1, Б=2, В=3 ...\n"
        "A - рік коли закінчую навчання\n Б - рік коли почали відносини\n В - рік коли ти закінчила 9 класс\n"
        f"Введи код",
        B_CIPHER
    )

# ===================== CIPHER =====================
@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == CIPHER)
def cipher(message):
    chat_id = message.chat.id
    admin_forward(message)
    track_user_msg(message, B_CIPHER)

    if message.text != CIPHER_RESULT:
        send_block(chat_id, "Майже… спробуй ще раз 🤍", B_CIPHER)
        return

    delete_block(chat_id, B_CIPHER)

    user_state[chat_id] = WAIT_60

    try:
        send_video_block(chat_id, VIDEO_DURING_WAIT60, "Поки чекаєш переглянь ще раз 🤍", B_WAIT60_MEDIA)
    except:
        send_block(chat_id, "⚠️ Не знайшов plm.mp4", B_WAIT60)

    send_block(chat_id, "⏳ ГРА 7: ТАЙМЕР ДОВІРИ\n\nНе пиши нічого 60 секунд…", B_WAIT60)
    threading.Thread(target=wait_unlock_60, args=(chat_id,), daemon=True).start()

def wait_unlock_60(chat_id):
    time.sleep(60)
    delete_block(chat_id, B_WAIT60)

    try:
        send_photo_block(chat_id, PHOTO_AFTER_WAIT60, "Замок відкрито 🤍", B_WAIT60_MEDIA)
    except:
        pass

    user_state[chat_id] = TRUTH_1
    truth_step[chat_id] = 1
    send_block(chat_id,
        "🎭 ГРА 8: ПРАВДА ЧИ СПОГАД (1/3)\n"
        "Відповідай чесно (мінімум 20 символів):\n"
        "Коли ти зрозуміла, що я важливий для тебе?",
        B_TRUTH
    )

# ===================== TRUTH 1-3 =====================
@bot.message_handler(func=lambda m: user_state.get(m.chat.id) in [TRUTH_1, TRUTH_2, TRUTH_3])
def truth_game(message):
    chat_id = message.chat.id
    admin_forward(message)
    track_user_msg(message, B_TRUTH)

    if len(message.text) < 20:
        send_block(chat_id, "Трошки більше… я хочу відчути твої слова 🤍", B_TRUTH)
        return

    st = user_state.get(chat_id)

    if st == TRUTH_1:
        send_block(
            chat_id,
            "Я зрозумів, коли ти мені відправила мішку і цукерки. "
            "Ти казала, що в цьому нема нічого такого, але це було вау 🤍",
            B_CODE_MEDIA
        )
        user_state[chat_id] = TRUTH_2
        send_block(chat_id, "🎭 (2/3)\nЩо ти тоді хотіла сказати мені, але не сказала?", B_TRUTH)

    elif st == TRUTH_2:
        send_block(
            chat_id,
            "Я ще у перший день хотів сказати, що ти просто неймовірна дівчинка, "
            "але боявся відпугнути від себе 😅",
            B_CODE_MEDIA
        )
        user_state[chat_id] = TRUTH_3
        send_block(chat_id, "🎭 (3/3)\nЯкий момент з нами ти хочеш повторити ще раз?", B_TRUTH)

    else:
        send_block(
            chat_id,
            "Я б хотів повторити нашу першу прогулянку — це було неймовірно 🤍",
            B_CODE_MEDIA
        )
        delete_block(chat_id, B_TRUTH)

        user_state[chat_id] = PHOTO_PATH
        photo_path_step[chat_id] = 0
        send_block(chat_id,
            "📸 ГРА 9: ФОТО-ШЛЯХ\n"
            "Надішли 3 фото по черзі.\n\n"
            "📸 1/3: Фото, де ти щаслива",
            B_PHOTOPATH
        )

# ===================== FINAL =====================
@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == FINAL)
def final(message):
    chat_id = message.chat.id
    admin_forward(message)
    track_user_msg(message, B_FINAL)

    send_block(chat_id,
        "Я дочекався цього моменту доки ти прошла всі питання 🤍\n\n"
        "Ти велика молодчинка!! 😽\n"
        "І я кохаю тебе безмежно 🫶 \n\n"
        "Квіточко моя, я не завжди можу дати тобі все, що ти захочеш. Ти знаєш, що зараз у мене непростий період із коштами, але я дуже стараюся знайти вихід і зробив цього бота спеціально для тебе — щоб ти завжди пам’ятала наші спогади й наші важливі дати 😅\n"
        "Я витратив на нього багато часу, і через це інколи відповідав тобі не так швидко й не міг нормально поговорити. Мені дуже шкода за це, і я хочу, щоб це стало маленькою компенсацією для тебе :)\n"
        "Я тебе дуже-дуже кохаю. Ти для мене одна з найрідніших і найважливіших дівчат у житті. Я хочу і буду для тебе найкращим. З 14 лютого 🫶🫶🫶",
        B_FINAL
    )

    # ✅ КНОПКА НА САЙТ (не прямая ссылка)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🌐 Відкрити сайт", url=SITE_URL))
    msg = bot.send_message(chat_id, "Натисни кнопку нижче 🤍", reply_markup=kb)
    track(chat_id, B_FINAL, msg.message_id)

    user_state.pop(chat_id, None)

# ===================== CATCH ALL =====================
@bot.message_handler(content_types=['text', 'photo', 'video', 'voice', 'document', 'sticker', 'audio'])
def catch_all(message):
    if message.chat.id == ADMIN_ID:
        return
    st = user_state.get(message.chat.id, "no_state")
    admin_log_text(
        f"📩 NEW\n"
        f"From: {message.from_user.first_name} ({message.chat.id})\n"
        f"State: {st}\n"
        f"Type: {message.content_type}"
    )
    admin_forward(message)

# ===================== RUN =====================
if __name__ == "__main__":
    print("Бот запущений...")
    bot.infinity_polling()
