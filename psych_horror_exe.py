import sys
import math
import random
import time
import os
import pygame

pygame.init()
try:
    pygame.mixer.init()
except pygame.error:
    pass

WIDTH, HEIGHT = 1100, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Психологический хоррор")
clock = pygame.time.Clock()

# ==========================================================
# Папка assets рядом с psych_horror.py — сюда добавляйте файлы.
# Карточки: klown.png, cucla.png
# Скримеры: skr.png, skr2.png, skr3.png, roulette_scare.png
# Мини-игра с клоуном: klwn21.png, klwn22.png, klwn23.png,
#                      clown_strip_music.wav
# Клоун/телефон: klwn2.png, clown_final.png, clown_voice.wav,
#                clown_laugh.wav, phone_music.mp3 (или soo.mp3),
#                phone_laugh.wav
# Рулетка: player_chair.png, roulette_clown.png, gun.png,
#          roulette_shot.wav, static.png
# Лес/финал: for.png, monst.png, monst2.png, monst3.png,
#            dark_room_music.mp3
# Таблетки: red_tablet.png или red.png (красная),
#           blue_tablet.png или blue.png (синяя)
# Новые мини-игры (синий/красный путь) картинок НЕ требуют —
# глаза, квадраты и двери рисуются кодом, скримеры берут
# старые skr2.png и skrsmx.mp3.
# Место для своих фонов помечено в коде: ### СЮДА МОЖНО ВСТАВИТЬ КАРТИНКУ ###
# ==========================================================

# Путь к ресурсам работает и из скрипта, и из собранного exe (PyInstaller).
if getattr(sys, "frozen", False):
    BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(BASE_DIR, "assets")

WHITE=(240,240,245); BLACK=(7,7,13); GRAY=(150,150,165)
RED=(175,20,35); GREEN=(35,120,65); BLUE=(45,125,235)
YELLOW=(225,185,40); WIRE_RED=(225,45,50); DARK=(35,35,50)
font_title=pygame.font.SysFont("arial",42,bold=True)
font=pygame.font.SysFont("arial",26)
font_small=pygame.font.SysFont("arial",19)
font_input=pygame.font.SysFont("arial",35)

STRIP_SPEED=9  # скорость белой полоски (была 6)

def load_image(filename, size=None):
    path = os.path.join(A, filename)
    if not os.path.exists(path):
        print("Не найдена картинка:", path)
        return None
    try:
        picture = pygame.image.load(path).convert_alpha()
        if size:
            picture = pygame.transform.smoothscale(picture, size)
        return picture
    except Exception as error:
        print("Ошибка загрузки:", path, error)
        return None

def load_sound(filename):
    path = os.path.join(A, filename)
    if not os.path.exists(path):
        print("Не найден звук:", path)
        return None
    try:
        return pygame.mixer.Sound(path)
    except Exception as error:
        print("Ошибка загрузки звука:", path, error)
        return None

class MusicTrack:
    """Фоновая музыка через pygame.mixer.music — mp3 играет надёжно."""
    def __init__(self, *filenames):
        self.path = None
        for name in filenames:
            path = os.path.join(A, name)
            if os.path.exists(path):
                self.path = path
                print("Фоновая музыка найдена:", path)
                break
        if self.path is None:
            print("Не найдена фоновая музыка ни под одним именем:", ", ".join(filenames))
    def play(self, loops=-1):
        if self.path:
            try:
                pygame.mixer.music.load(self.path)
                pygame.mixer.music.play(loops)
            except pygame.error as error:
                print("Ошибка воспроизведения музыки:", self.path, error)
    def stop(self):
        pygame.mixer.music.stop()

# Загрузка картинок
full_scare = load_image("skr2.png", (WIDTH, HEIGHT))
corner_scare = load_image("skr.png", (220, 175))
clown_image = load_image("klwn2.png", (350, 350))
clown_card_image = load_image("klown.png", (58, 58))
doll_image = load_image("cucla.png", (58, 58))

roulette_scare = load_image("roulette_scare.png", (WIDTH, HEIGHT))
static_image = load_image("static.png", (WIDTH, HEIGHT))
forest_image = load_image("for.png", (WIDTH, HEIGHT))

window_monsters = {
    1: load_image("monst.png", (360, 430)),
    2: load_image("monst2.png", (360, 430)),
    4: load_image("monst3.png", (360, 430)),
}

room_monster = load_image("skr3.png", (480, 560))
player_chair = load_image("player_chair.png", (250, 350))
roulette_clown = load_image("roulette_clown.png", (300, 380))
gun_image = load_image("gun.png", (230, 110))

strip_clowns = [
    load_image("klwn21.png", (430, 430)),
    load_image("klwn22.png", (430, 430)),
    load_image("klwn23.png", (430, 430)),
]

clown_final = load_image("clown_final.png", (430, 430))

# Таблетки: положи в assets red_tablet.png и blue_tablet.png (или red.png/blue.png).
red_pill = load_image("red_tablet.png", (120, 62)) or load_image("red.png", (120, 62))
blue_pill = load_image("blue_tablet.png", (120, 62)) or load_image("blue.png", (120, 62))

# Фоновая музыка — через mixer.music (mp3 играет надёжно).
# Телефонная музыка ищется и как soo.mp3, и как phone_music.mp3.
phone_music = MusicTrack("phone_music.mp3", "soo.mp3")
horror_music = MusicTrack("kol.mp3")
dark_music = MusicTrack("ujs.mp3")

scream_sound = load_sound("skrsmx.mp3")
roulette_sound = load_sound("roulette_shot.wav")
strip_music = load_sound("clown_strip_music.wav")
clown_voice = load_sound("smx2.mp3")
clown_laugh = load_sound("smx.mp3")
phone_laugh = load_sound("smx20.mp3")

EASY=[
("Сколько месяцев в году имеют 28 дней?",["Один","Два","Двенадцать"],2),
("Что принадлежит тебе, но другие используют чаще?",["Имя","Телефон","Дом"],0),
("У чего есть шея, но нет головы?",["У бутылки","У человека","У стола"],0),
("Что становится мокрым, пока сушит?",["Полотенце","Дождь","Снег"],0),
("Какой рукой лучше размешивать чай?",["Правой","Левой","Ложкой"],2),
("Что имеет зубы, но не кусается?",["Расчёска","Собака","Нож"],0),
]
HARD=[
("У фермера было 17 овец. Все, кроме 9, убежали. Сколько осталось?",["8","9","17"],1),
("Что можно сломать одним словом?",["Обещание","Камень","Окно"],0),
("Что имеет города, но не имеет домов?",["Карта","Книга","Телефон"],0),
("Что всегда увеличивается и никогда не уменьшается?",["Возраст","Рост","Температура"],0),
("Чем больше из неё берёшь, тем больше она становится?",["Яма","Коробка","Комната"],0),
]
CLOWN_Q=[
("Тебе нравятся клоуны?",["Да","Не очень","Нет"],0,1),
("Что ты сделаешь, если я улыбнусь?",["Улыбнусь","Убегу","Замру"],0,1),
("Кто сейчас смотрит на тебя?",["Никто","Ты","Моя тень"],1,0),
]
FINAL_Q=("Кто из нас выйдет отсюда?",["Я","Ты"],1)

state="menu"; running=True; attempts=3; phase_count=0
question=None; q_started=0.; q_limit=15.; used=set(); message=""
corner=False; corner_until=0.; next_corner=0.
wires=[]; wire_started=0.; wire_errors=0; wire_drag=None
cards=[]; lives=3; clowns_found=0; consecutive_dolls=0; box_scare_until=0.
anger=100; clown_qi=0; voice_until=0.; voice_waiting=False; laugh_until=0.
strip_hits=0; strip_misses=0; strip_target=pygame.Rect(0,0,0,0); strip_x=170.; strip_dir=1; strip_started=0.; strip_fail_until=0.
player_lives=2; enemy_lives=2; roulette_turn="player"; roulette_msg=""; roulette_spray=None; roulette_winner=None; roulette_next=0.
phone_lines=[]; phone_li=0; phone_chars=0; phone_next=0.; phone_after=""
window_count=0; window_next=0.; dark_until=0.; word_input=""; word_feedback_until=0.
letter_index=0; letter_positions=[]; clown_intro_until=0.
letter_deadline=0.
# Печать вопросов клоуна по буквам (как сообщения на телефоне)
talk_text=""; talk_shown=0; talk_next=0.; talk_done=False
final_shown=0; final_next=0.; final_done=False
gun_angle=0.  # текущий угол поворота пистолета на рулетке
blood_until=0.

# --- Таблетки ---
# Красная расположена ВЫШЕ (y=500), синяя НИЖЕ (y=568) — на языке монстра.
# Если язык на твоём skr3.png в другом месте — просто поправь координаты ниже.
RED_TABLET_POS=(WIDTH//2, 500)
BLUE_TABLET_POS=(WIDTH//2, 568)
TABLET_BASE_SIZE=(120, 62)   # базовый размер таблетки
TABLET_HOVER=1.25            # во сколько раз увеличивается при наведении
tablet_scales={"red":1.0, "blue":1.0}   # текущий масштаб (плавная анимация)
tablet_rects={}              # зоны клика (пересчитываются каждый кадр)

# --- Мини-игры пути (синяя/красная таблетка) ---
tablet_choice=None
minis=[]; mini_index=0; mini_scare_until=0.; mini_done_until=0.
M={}  # состояние текущей мини-игры

def draw_text(s,f,c,center,maxw=None):
    words=s.split(); lines=[]; line=""
    for word in words:
        candidate=(line+" "+word).strip()
        if maxw and f.size(candidate)[0]>maxw and line:
            lines.append(line); line=word
        else: line=candidate
    if line: lines.append(line)
    h=f.get_linesize(); y=center[1]-len(lines)*h//2
    for i,l in enumerate(lines):
        surf=f.render(l,True,c); screen.blit(surf,surf.get_rect(center=(center[0],y+i*h+h//2)))

def draw_button(rect,label,color=DARK):
    pygame.draw.rect(screen,color,rect,border_radius=9); pygame.draw.rect(screen,GRAY,rect,2,border_radius=9); draw_text(label,font,WHITE,rect.center,rect.width-14)

def point_near(p,c,r=32): return math.hypot(p[0]-c[0],p[1]-c[1])<=r

def select_question(pool):
    global question,q_started,corner
    available=[q for q in pool if q[0] not in used]
    if not available: used.clear(); available=pool[:]
    question=random.choice(available); used.add(question[0]); q_started=time.time(); corner=False

def start_easy():
    global state,attempts,phase_count,q_limit
    state="easy"; attempts=3; phase_count=0; q_limit=15.; used.clear()
    # На всякий случай глушим всю фоновую музыку перед новой партией.
    phone_music.stop()
    if phone_laugh: phone_laugh.stop()
    horror_music.stop()
    select_question(EASY)

def lose_attempt(text):
    global attempts,state,message
    attempts-=1; message=text
    horror_music.stop()
    state="dead" if attempts<=0 else "lost"

def make_wires():
    global wires
    colors=[BLUE,WIRE_RED,YELLOW]; ly=[250,350,450]; ry=ly[:]; random.shuffle(ry)
    wires=[{"color":colors[i],"left":(170,ly[i]),"right":(WIDTH-170,ry[i]),"connected":False} for i in range(3)]

def start_wires():
    global state,wire_started,wire_errors,wire_drag
    state="wires"; wire_errors=0; wire_drag=None; make_wires(); wire_started=time.time()

def start_hard():
    global state,phase_count,next_corner
    state="hard"; phase_count=0; used.clear()
    next_corner=time.time()+random.uniform(2,5)  # скример вылезает чаще
    horror_music.play()
    select_question(HARD)

def start_cards():
    global state,cards,lives,clowns_found,consecutive_dolls
    horror_music.stop()
    state="cards"; lives=3; clowns_found=0; consecutive_dolls=0
    types=["clown"]*15+["doll"]*15; random.shuffle(types)
    mx,my,gx,gy,cols=25,105,8,8,6; cw=(WIDTH-2*mx-(cols-1)*gx)//cols; ch=94; cards=[]
    for i,kind in enumerate(types):
        row,col=divmod(i,cols); rect=pygame.Rect(mx+col*(cw+gx),my+row*(ch+gy),cw,ch); cards.append({"kind":kind,"rect":rect,"open":False})

def start_clown_talk():
    global state,anger,clown_qi,voice_waiting,voice_until
    state="clown_talk"; anger=100; clown_qi=0; voice_waiting=True; voice_until=play_for(clown_voice,random.uniform(1,3))

def play_for(sound_obj,duration):
    if sound_obj: sound_obj.stop(); sound_obj.play(); return time.time()+duration
    return time.time()

def start_strip():
    global state,strip_hits,strip_misses,strip_x,strip_dir
    state="strip"; strip_hits=0; strip_misses=0; strip_x=170.; strip_dir=1; new_strip_target()

def new_strip_target():
    global strip_target,strip_x,strip_dir,strip_started
    strip_target=pygame.Rect(random.randint(210,WIDTH-360),540,random.randint(55,90),28); strip_x=170.; strip_dir=1; strip_started=time.time()

def miss_strip():
    global strip_misses,state,strip_fail_until
    strip_misses+=1
    if strip_misses>=2:
        state="strip_fail"; strip_fail_until=time.time()+3
        if strip_music: strip_music.play()
    else: new_strip_target()

def start_roulette():
    global state,player_lives,enemy_lives,roulette_turn,roulette_msg,roulette_spray,roulette_winner,roulette_next
    state="roulette"; player_lives=2; enemy_lives=2; roulette_turn="player"; roulette_msg="Выбери, в кого стрелять."; roulette_spray=None; roulette_winner=None; roulette_next=0

def start_phone(lines,after):
    global state,phone_lines,phone_li,phone_chars,phone_next,phone_after
    state="phone"; phone_lines=lines; phone_li=0; phone_chars=0; phone_next=time.time()+.1; phone_after=after
    phone_music.play()
    if phone_laugh: phone_laugh.play(-1)

def start_window():
    global state,window_count,window_next
    state="window"; window_count=0; window_next=time.time()+3

def start_dark_room():
    global state,dark_until
    state="dark_room"; dark_until=time.time()+2
    dark_music.play()

def start_new_clown():
    """Единая точка входа в сцену букв: все счётчики сбрасываются всегда."""
    global state,clown_intro_until,letter_index,letter_positions,letter_deadline,word_input
    state="new_clown"; clown_intro_until=time.time()+2
    letter_index=0; letter_positions=[]; letter_deadline=0.; word_input=""

def roulette_shot(target):
    global player_lives,enemy_lives,roulette_msg,roulette_spray,roulette_winner,roulette_turn,state,roulette_next
    if random.random()<.60:
        roulette_spray=target; roulette_msg="Выстрел!"
        if roulette_sound: roulette_sound.play()
        if target=="player": player_lives-=1
        else: enemy_lives-=1
    else: roulette_spray=None; roulette_msg="Осечка."
    if player_lives<=0: roulette_winner="clown"; state="roulette_scare"; roulette_next=time.time()+2
    elif enemy_lives<=0: roulette_winner="player"; start_phone(["А ты молодец","Не плохо держишься"],"window")
    else: roulette_turn="clown" if roulette_turn=="player" else "player"; roulette_next=time.time()+.8 if roulette_turn=="clown" else 0

def answer_question(i):
    global phase_count,q_limit
    if i!=question[2]: lose_attempt("Неверный ответ. Попытка потеряна."); return
    q_limit=max(5.,q_limit-(time.time()-q_started)*.3); phase_count+=1
    if state=="easy" and phase_count>=3: start_wires()
    elif state=="hard" and phase_count>=3: start_cards()
    else: select_question(EASY if state=="easy" else HARD)

def show_corner():
    global corner,corner_until,next_corner
    corner=True; corner_until=time.time()+3; next_corner=time.time()+random.uniform(2,5)  # чаще, чем было
    if scream_sound: scream_sound.play()

def update_tablets():
    """Плавное увеличение таблетки под курсором и уменьшение, когда мышь ушла."""
    global tablet_scales, tablet_rects
    mouse=pygame.mouse.get_pos()
    for name,pos,base in (("red",RED_TABLET_POS,TABLET_BASE_SIZE),("blue",BLUE_TABLET_POS,TABLET_BASE_SIZE)):
        w,h=int(TABLET_BASE_SIZE[0]*tablet_scales[name]),int(TABLET_BASE_SIZE[1]*tablet_scales[name])
        rect=pygame.Rect(0,0,w,h); rect.center=pos
        tablet_rects[name]=rect
        target=TABLET_HOVER if rect.collidepoint(mouse) else 1.0
        tablet_scales[name]+=(target-tablet_scales[name])*0.18  # плавность

# ==========================================================
# МИНИ-ИГРЫ ПУТИ (психологическая путаница со скримерами)
# Провал — скример и перезапуск мини-игры (попытки не тратятся).
# ==========================================================

def mini_fail(msg=""):
    """Провал мини-игры: полноэкранный скример, потом перезапуск этой же игры."""
    global state, mini_scare_until
    state="mini_scare"; mini_scare_until=time.time()+1.5; M.clear(); M["fail_msg"]=msg
    if scream_sound: scream_sound.play()

def mini_done():
    """Мини-игра пройдена — переходим к следующей или к концовке пути."""
    global mini_index, state, mini_done_until
    mini_index+=1
    if mini_index>=len(minis):
        horror_music.stop()
        state="blue_win" if tablet_choice=="blue" else "red_win"
    else:
        state="mini_done"; mini_done_until=time.time()+1.3

def next_mini():
    global state
    M.clear()
    minis[mini_index]["start"]()
    state="mini"

def start_minis(choice):
    global tablet_choice, minis, mini_index, state
    tablet_choice=choice
    minis = BLUE_MINIS if choice=="blue" else RED_MINIS
    mini_index=0
    horror_music.play()
    M.clear()
    minis[0]["start"]()
    state="mini"

# ---------- СИНИЙ ПУТЬ (проще) ----------

# 1. «Не нажимай кнопку» — держись 8 секунд, кнопка врёт, что нажать безопасно
def b1_start():
    M["end"]=time.time()+8; M["btn"]=pygame.Rect(WIDTH//2-180,300,360,80)
def b1_handle(e):
    if e.type==pygame.MOUSEBUTTONDOWN and e.button==1 and M["btn"].collidepoint(e.pos):
        mini_fail("Тебе же сказали не нажимать.")
def b1_update(now):
    if now>=M["end"]: mini_done()
def b1_draw():
    pygame.draw.rect(screen,(20,20,28),(0,0,WIDTH,HEIGHT))
    left=max(0,M["end"]-time.time())
    pygame.draw.rect(screen,(60,60,80),(WIDTH//2-260,560,520,26),border_radius=6)
    pygame.draw.rect(screen,BLUE,(WIDTH//2-260,560,int(520*left/8),26),border_radius=6)
    phase=int(time.time()*2)%2
    if phase: draw_text("НЕ НАЖИМАЙ ЭТУ КНОПКУ",font_title,WHITE,(WIDTH//2,170))
    else: draw_text("НАЖМИ ИЛИ УМРЁШЬ (ЭТО ЛОЖЬ)",font_title,RED,(WIDTH//2,170))
    draw_text("Продержись 8 секунд",font_small,GRAY,(WIDTH//2,240))
    draw_button(M["btn"],"НАЖМИ МЕНЯ (ЭТО БЕЗОПАСНО)",RED if phase else DARK)

# 2. «Правда или ложь» — утверждения с подвохом
B2_Q=[("Дважды два — четыре.",True),("Луна сделана из сыра.",False),
("У змеи нет ног.",True),("Ты сейчас в полной безопасности.",False),("Птицы умеют летать.",True)]
def b2_start(): M["i"]=0; M["wrong"]=0
def b2_handle(e):
    if e.type!=pygame.MOUSEBUTTONDOWN or e.button!=1: return
    said=None
    if pygame.Rect(WIDTH//2-260,480,240,70).collidepoint(e.pos): said=True
    elif pygame.Rect(WIDTH//2+20,480,240,70).collidepoint(e.pos): said=False
    else: return
    if said==B2_Q[M["i"]][1]:
        M["i"]+=1
        if M["i"]>=len(B2_Q): mini_done()
    else: mini_fail("Клоун лжёт не только тебе.")
def b2_update(now): pass
def b2_draw():
    draw_text(f"Правда или ложь?  Вопрос {M['i']+1}/{len(B2_Q)}",font,WHITE,(WIDTH//2,120))
    draw_text(B2_Q[M["i"]][0],font_title,WHITE,(WIDTH//2,260),WIDTH-140)
    draw_button(pygame.Rect(WIDTH//2-260,480,240,70),"ПРАВДА",GREEN)
    draw_button(pygame.Rect(WIDTH//2+20,480,240,70),"ЛОЖЬ",RED)
    draw_text("Одна ошибка — провал",font_small,GRAY,(WIDTH//2,600))

# 3. «Найди не такой» — один квадрат чуть другого оттенка, сетка мигает
def b3_start(): M["round"]=0; b3_regen()
def b3_regen():
    base=random.randint(55,110); M["base"]=(base,base,base)
    delta=random.choice([22,26,30])
    M["odd_color"]=(min(255,base+delta),)*3 if random.random()<.5 else (max(0,base-delta),)*3
    M["odd_index"]=random.randrange(9); M["gen"]=time.time()
    M["cells"]=[pygame.Rect(200+(i%3)*240,200+(i//3)*150,220,130) for i in range(9)]
def b3_handle(e):
    if e.type!=pygame.MOUSEBUTTONDOWN or e.button!=1: return
    for i,c in enumerate(M["cells"]):
        if c.collidepoint(e.pos):
            if i==M["odd_index"]:
                M["round"]+=1
                if M["round"]>=3: mini_done()
                else: b3_regen()
            else: mini_fail("Не тот квадрат.")
            return
def b3_update(now):
    if time.time()-M["gen"]>=1.0: b3_regen()
def b3_draw():
    draw_text(f"Найди квадрат другого оттенка. Раунд {M['round']+1}/3",font,WHITE,(WIDTH//2,120))
    draw_text("Клетки меняются каждую секунду!",font_small,GRAY,(WIDTH//2,160))
    for i,c in enumerate(M["cells"]):
        pygame.draw.rect(screen,M["base"] if i!=M["odd_index"] else M["odd_color"],c,border_radius=6)

# 4. «Считай клоунов» — лица мелькают 6 секунд, потом вопрос
def b4_start(): M["round"]=0; b4_round()
def b4_round():
    M["phase"]="show"; M["count"]=0; M["end_show"]=time.time()+6
    M["next_face"]=0.; M["face_until"]=0.; M["face_pos"]=(0,0)
def b4_handle(e):
    if M["phase"]!="ask" or e.type!=pygame.MOUSEBUTTONDOWN or e.button!=1: return
    for i,b in enumerate(M["choices"]):
        if b.collidepoint(e.pos):
            if i==M["correct_index"]:
                M["round"]+=1
                if M["round"]>=2: mini_done()
                else: b4_round()
            else: mini_fail("Ты не умеешь считать клоунов.")
            return
def b4_update(now):
    if M["phase"]!="show": return
    if now>=M["end_show"]:
        M["phase"]="ask"
        correct=M["count"]
        opts=[correct,correct+1,correct+2,correct+3]; random.shuffle(opts)
        M["correct_index"]=opts.index(correct); M["opts"]=opts
        M["choices"]=[pygame.Rect(WIDTH//2-220+i*115,420,105,60) for i in range(4)]
    elif now>=M["next_face"]:
        M["count"]+=1; M["face_until"]=now+0.3
        M["next_face"]=now+random.uniform(0.5,0.9)
        M["face_pos"]=(random.randint(120,WIDTH-120),random.randint(180,HEIGHT-200))
def b4_draw():
    if M["phase"]=="show":
        draw_text("Считай клоунов!",font_title,WHITE,(WIDTH//2,110))
        if time.time()<M["face_until"]:
            faces=[x for x in strip_clowns if x] or ([clown_card_image] if clown_card_image else [])
            if faces:
                img=random.choice(faces)
                screen.blit(img,img.get_rect(center=M["face_pos"]))
            else: pygame.draw.circle(screen,RED,M["face_pos"],60)
    else:
        draw_text("Сколько клоунов ты видел?",font_title,WHITE,(WIDTH//2,140))
        for i,b in enumerate(M["choices"]): draw_button(b,str(M["opts"][i]))

# 5. «Светофор» — жми только когда горит зелёный, темп ускоряется
def b5_start():
    M["need"]=6; M["got"]=0; M["miss"]=0
    M["is_green"]=False; M["interval"]=1.0; M["next"]=time.time()+0.8; M["green_until"]=0.
def b5_handle(e):
    if e.type!=pygame.MOUSEBUTTONDOWN or e.button!=1: return
    if M["is_green"]:
        M["got"]+=1; M["interval"]=max(0.5,M["interval"]-0.08)
        M["is_green"]=False; M["next"]=time.time()+M["interval"]
        if M["got"]>=M["need"]: mini_done()
    else: mini_fail("Зелёный был не сейчас.")
def b5_update(now):
    if M["is_green"]:
        if now>=M["green_until"]:  # зелёный пропущен
            M["miss"]+=1
            if M["miss"]>=2: mini_fail("Ты пропустил зелёный.")
            else:
                M["is_green"]=False; M["next"]=now+M["interval"]
    elif now>=M["next"]:
        M["is_green"]=True
        M["green_until"]=now+max(0.5,M["interval"]*0.8)
def b5_draw():
    draw_text("Нажимай ТОЛЬКО когда горит зелёный",font,WHITE,(WIDTH//2,110))
    draw_text(f"Зелёных: {M['got']}/{M['need']}   Пропущено: {M['miss']}/2",font_small,GRAY,(WIDTH//2,150))
    color=GREEN if M["is_green"] else (60,60,70)
    pygame.draw.rect(screen,color,(WIDTH//2-140,260,280,280),border_radius=14)
    if not M["is_green"]: draw_text("ЖДИ",font_title,GRAY,(WIDTH//2,400))

# 6. «Замри» — три фазы, когда нельзя двигать мышью (с помехами)
def b6_start(): M["phase"]=0; M["rest"]=0.; b6_freeze()
def b6_freeze():
    M["anchor"]=pygame.mouse.get_pos(); M["until"]=time.time()+2.5; M["phase"]+=1
def b6_handle(e):
    if e.type==pygame.MOUSEMOTION and M["until"]>time.time():
        if math.hypot(e.pos[0]-M["anchor"][0],e.pos[1]-M["anchor"][1])>18:
            mini_fail("Ты дрогнул.")
def b6_update(now):
    if M["rest"] and now<M["rest"]: return
    if M["rest"]:
        M["rest"]=0.; b6_freeze(); return
    if now>=M["until"]:
        if M["phase"]>=3: mini_done()
        else: M["rest"]=now+1.3
def b6_draw():
    if time.time()<M["until"]:
        draw_text(f"НЕ ДВИГАЙ МЫШЬЮ! Фаза {M['phase']}/3",font_title,RED,(WIDTH//2,140))
        draw_text("Замри...",font,WHITE,(WIDTH//2,300))
        left=max(0,M["until"]-time.time())
        pygame.draw.rect(screen,(60,60,80),(WIDTH//2-260,470,520,26),border_radius=6)
        pygame.draw.rect(screen,RED,(WIDTH//2-260,470,int(520*left/2.5),26),border_radius=6)
        if random.random()<0.3: pygame.draw.circle(screen,RED,(random.randint(50,WIDTH-50),random.randint(200,600)),random.randint(8,25))
    else:
        draw_text(f"Передышка ({M['phase']}/3 пройдено)",font_title,GREEN,(WIDTH//2,140))
        draw_text("Дальше снова замрёшь...",font,GRAY,(WIDTH//2,300))

BLUE_MINIS=[
{"name":"Не нажимай кнопку","start":b1_start,"handle":b1_handle,"update":b1_update,"draw":b1_draw},
{"name":"Правда или ложь","start":b2_start,"handle":b2_handle,"update":b2_update,"draw":b2_draw},
{"name":"Найди не такой","start":b3_start,"handle":b3_handle,"update":b3_update,"draw":b3_draw},
{"name":"Считай клоунов","start":b4_start,"handle":b4_handle,"update":b4_update,"draw":b4_draw},
{"name":"Светофор","start":b5_start,"handle":b5_handle,"update":b5_update,"draw":b5_draw},
{"name":"Замри","start":b6_start,"handle":b6_handle,"update":b6_update,"draw":b6_draw},
]

# ---------- КРАСНЫЙ ПУТЬ (сложнее) ----------

# 1. «Симон говорит» — выполнять только команды с «Симон говорит», есть ловушки
R1_CMDS=[("Симон говорит: нажми ЛЕВО","left",True),
("Симон говорит: нажми ПРАВО","right",True),
("Нажми ЛЕВО","left",False),
("Нажми ПРАВО","right",False),
("НАЖМИ ЛЕВО ЧТОБЫ ВЫЖИТЬ","left",False),
("СИМОН ГОВОРИТ: нажми ПРАВО","right",True),
("Быстро нажми ПРАВО","right",False),
("Симон говорит: нажми ЛЕВО СЕЙЧАС","left",True)]
def r1_start(): M["i"]=0; M["wrong"]=0; r1_next()
def r1_next():
    M["cmd"]=random.choice(R1_CMDS); M["until"]=time.time()+1.6
def r1_handle(e):
    if e.type!=pygame.MOUSEBUTTONDOWN or e.button!=1: return
    side=None
    if pygame.Rect(WIDTH//2-320,540,280,80).collidepoint(e.pos): side="left"
    elif pygame.Rect(WIDTH//2+40,540,280,80).collidepoint(e.pos): side="right"
    else: return
    if not M["cmd"][2] or side!=M["cmd"][1]:
        M["wrong"]+=1
        if M["wrong"]>=2: mini_fail("Симон разочарован.")
        else: r1_next()
    else:
        M["i"]+=1
        if M["i"]>=8: mini_done()
        else: r1_next()
def r1_update(now):
    if now>=M["until"]:
        if M["cmd"][2]:  # требовалось нажать — просрочил
            M["wrong"]+=1
            if M["wrong"]>=2: mini_fail("Симон разочарован.")
            else: r1_next()
        else: r1_next()
def r1_draw():
    draw_text("СИМОН ГОВОРИТ",font_title,WHITE,(WIDTH//2,90))
    draw_text(f"Команда {M['i']+1}/8   Ошибок: {M['wrong']}/2   Выполняй только «Симон говорит»",font_small,GRAY,(WIDTH//2,140))
    if random.random()<0.05: screen.fill((90,0,10))  # вспышка-пугалка
    draw_text(M["cmd"][0],font_title,YELLOW if M["cmd"][2] else RED,(WIDTH//2,300),WIDTH-120)
    left=max(0,M["until"]-time.time())
    pygame.draw.rect(screen,(60,60,80),(WIDTH//2-260,480,520,20),border_radius=6)
    pygame.draw.rect(screen,YELLOW,(WIDTH//2-260,480,int(520*left/1.6),20),border_radius=6)
    draw_button(pygame.Rect(WIDTH//2-320,540,280,80),"ЛЕВО")
    draw_button(pygame.Rect(WIDTH//2+40,540,280,80),"ПРАВО")

# 2. «Наоборот» — инструкция меняется: то выбирай неверный, то верный ответ
R2_Q=[("Сколько будет 2+2?",["4","5","6"],0),
("Какого цвета небо днём?",["Синего","Зелёного","Красного"],0),
("Сколько ног у паука?",["Восемь","Шесть","Десять"],0),
("Столица России?",["Москва","Париж","Тула"],0),
("Сколько будет 5×5?",["25","24","26"],0)]
def r2_start():
    M["i"]=0; M["wrong"]=0; M["invert"]=False
    M["btns"]=[pygame.Rect(WIDTH//2-250,340+k*90,500,70) for k in range(3)]
def r2_handle(e):
    if e.type!=pygame.MOUSEBUTTONDOWN or e.button!=1: return
    q=R2_Q[M["i"]]
    for j,b in enumerate(M["btns"]):
        if b.collidepoint(e.pos):
            good=(j==q[2]) if M["invert"] else (j!=q[2])
            if good:
                M["i"]+=1
                if M["i"]>=len(R2_Q): mini_done()
                else:
                    M["invert"]=random.random()<0.4
                    M["btns"]=[pygame.Rect(WIDTH//2-250,340+k*90,500,70) for k in range(3)]
            else:
                M["wrong"]+=1
                if M["wrong"]>=2: mini_fail("Путаница победила.")
            return
def r2_update(now): pass
def r2_draw():
    draw_text("ПУТАНИЦА: ЧИТАЙ ИНСТРУКЦИЮ КАЖДЫЙ РАЗ",font_small,YELLOW,(WIDTH//2,80))
    instr="ВЫБЕРИ ПРАВИЛЬНЫЙ ОТВЕТ" if M["invert"] else "ВЫБЕРИ НЕПРАВИЛЬНЫЙ ОТВЕТ"
    draw_text(instr,font_title,GREEN if M["invert"] else RED,(WIDTH//2,150))
    draw_text(R2_Q[M["i"]][0],font,WHITE,(WIDTH//2,260))
    draw_text(f"Вопрос {M['i']+1}/{len(R2_Q)}   Ошибок: {M['wrong']}/2",font_small,GRAY,(WIDTH//2,320))
    for j,b in enumerate(M["btns"]): draw_button(b,R2_Q[M["i"]][1][j])

# 3. «Память со страхом» — 12 карточек, после каждой ошибки красная вспышка
def r3_start():
    letters=["А","Б","В","Г","Д","Е"]*2; random.shuffle(letters)
    M["cards"]=[{"ch":letters[i],"open":False,"done":False} for i in range(12)]
    M["open"]=[]; M["wrong"]=0; M["flip_at"]=0.; M["flash_until"]=0.
def r3_rect(idx): return pygame.Rect(60+(idx%4)*250,180+(idx//4)*160,230,140)
def r3_handle(e):
    if e.type!=pygame.MOUSEBUTTONDOWN or e.button!=1 or time.time()<M["flash_until"]: return
    for idx,c in enumerate(M["cards"]):
        if r3_rect(idx).collidepoint(e.pos) and not c["open"] and not c["done"]:
            c["open"]=True; M["open"].append(idx)
            if len(M["open"])==2:
                a,b=M["open"]
                if M["cards"][a]["ch"]==M["cards"][b]["ch"]:
                    M["cards"][a]["done"]=M["cards"][b]["done"]=True; M["open"]=[]
                    if all(x["done"] for x in M["cards"]): mini_done()
                else:
                    M["wrong"]+=1
                    if M["wrong"]>=8: mini_fail("Память тебя подвела.")
                    else: M["flip_at"]=time.time()+0.8; M["flash_until"]=time.time()+0.45
            break
def r3_update(now):
    if M["flip_at"] and now>=M["flip_at"]:
        for idx in M["open"]: M["cards"][idx]["open"]=False
        M["open"]=[]; M["flip_at"]=0.
def r3_draw():
    draw_text(f"Найди все пары. Ошибок: {M['wrong']}/8",font,WHITE,(WIDTH//2,120))
    for idx,c in enumerate(M["cards"]):
        rect=r3_rect(idx)
        if c["done"] or c["open"]:
            pygame.draw.rect(screen,(30,30,40),rect,border_radius=8)
            pygame.draw.rect(screen,GREEN if c["done"] else GRAY,rect,2,border_radius=8)
            draw_text(c["ch"],font_title,WHITE,rect.center)
        else:
            pygame.draw.rect(screen,(70,45,35),rect,border_radius=8)
            pygame.draw.rect(screen,GRAY,rect,2,border_radius=8); draw_text("?",font_title,WHITE,rect.center)
    if time.time()<M["flash_until"]:
        screen.fill((140,0,15))  # красная вспышка после ошибки

# 4. «Глаза в темноте» — попадай кликом по движущимся глазам
def r4_start(): M["hits"]=0; M["miss"]=0; r4_eye()
def r4_eye():
    M["pos"]=[random.randint(80,WIDTH-80),random.randint(150,HEIGHT-120)]
    M["born"]=time.time(); M["life"]=0.9
    M["drift"]=time.time()+0.15
    M["vel"]=[random.choice([-3,-2,2,3]),random.choice([-2,-1,1,2])]
def r4_handle(e):
    if e.type!=pygame.MOUSEBUTTONDOWN or e.button!=1: return
    ex,ey=M["pos"]
    if math.hypot(e.pos[0]-ex,e.pos[1]-ey)<=45:
        M["hits"]+=1
        if M["hits"]>=7: mini_done()
        else: r4_eye()
    else:
        M["miss"]+=1
        if M["miss"]>=3: mini_fail("Глаза смотрели на тебя.")
def r4_update(now):
    if now>=M["born"]+M["life"]:
        M["miss"]+=1
        if M["miss"]>=3: mini_fail("Глаза смотрели на тебя."); return
        else: r4_eye()
    if "drift" not in M: return  # после провала состояние очищено — выходим
    if now>=M["drift"]:
        M["pos"][0]=max(60,min(WIDTH-60,M["pos"][0]+M["vel"][0]))
        M["pos"][1]=max(140,min(HEIGHT-80,M["pos"][1]+M["vel"][1]))
        M["drift"]=now+0.15
def r4_draw():
    screen.fill((4,4,8))
    if random.random()<0.02: screen.fill((60,0,8))  # мигание
    # ### СЮДА МОЖНО ВСТАВИТЬ КАРТИНКУ ### — фона темноты, например: dark_bg.png
    ex,ey=M["pos"]
    pygame.draw.ellipse(screen,(235,235,225),(int(ex)-40,int(ey)-22,80,44))
    pygame.draw.circle(screen,(150,20,25),(int(ex),int(ey)),11)
    pygame.draw.circle(screen,BLACK,(int(ex),int(ey)),4)
    draw_text(f"Попади в глаза: {M['hits']}/7   Промахи: {M['miss']}/3",font_small,GRAY,(WIDTH//2,80))

# 5. «Перевёртыш» — вводи число задом наперёд, на фоне мелькают скримеры
def r5_start(): M["i"]=0; M["wrong"]=0; r5_new()
def r5_new():
    n=random.randint(100,999)
    M["num"]=n; M["target"]=int(str(n)[::-1]); M["text"]=""
    M["end"]=time.time()+7
def r5_handle(e):
    if e.type==pygame.KEYDOWN:
        if e.key==pygame.K_BACKSPACE: M["text"]=M["text"][:-1]
        elif e.key in (pygame.K_RETURN,pygame.K_KP_ENTER):
            if M["text"].strip() and M["text"].isdigit() and int(M["text"])==M["target"]:
                M["i"]+=1
                if M["i"]>=5: mini_done()
                else: r5_new()
            else:
                M["wrong"]+=1
                if M["wrong"]>=2: mini_fail("Цифры обманули тебя.")
                else: r5_new()
        elif e.unicode and e.unicode.isdigit() and len(M["text"])<3: M["text"]+=e.unicode
def r5_update(now):
    if now>=M["end"]:
        M["wrong"]+=1
        if M["wrong"]>=2: mini_fail("Время вышло.")
        else: r5_new()
def r5_draw():
    draw_text("ВВЕДИ ЧИСЛО ЗАДОМ НАПЕРЁД",font_title,WHITE,(WIDTH//2,100))
    draw_text(f"Число {M['i']+1}/5   Ошибок: {M['wrong']}/2",font_small,GRAY,(WIDTH//2,150))
    draw_text(str(M["num"]),font_input,WHITE,(WIDTH//2,280))
    pygame.draw.rect(screen,WHITE,(WIDTH//2-160,360,320,70))
    draw_text(M["text"] or "_",font_input,BLACK,(WIDTH//2,395))
    left=max(0,M["end"]-time.time())
    pygame.draw.rect(screen,(60,60,80),(WIDTH//2-260,480,520,20),border_radius=6)
    pygame.draw.rect(screen,RED,(WIDTH//2-260,480,int(520*left/7),20),border_radius=6)
    if random.random()<0.04:
        faces=[x for x in strip_clowns if x]
        if faces: screen.blit(random.choice(faces),(random.randint(0,WIDTH-300),random.randint(150,450)))

# 6. «Три двери» — за некоторыми дверями скримеры, 3 скримера = смерть
def r6_start(): M["i"]=0; M["traps_hit"]=0; M["trap_until"]=0.
def r6_handle(e):
    if e.type!=pygame.MOUSEBUTTONDOWN or e.button!=1: return
    if M["trap_until"]>time.time():
        M["trap_until"]=0.; M["i"]+=1
        if M["i"]>=5: mini_done()
        return
    for d in range(3):
        if pygame.Rect(WIDTH//2-390+d*270,240,240,330).collidepoint(e.pos):
            if random.random()<0.45:  # за дверью скример
                M["traps_hit"]+=1
                if M["traps_hit"]>=3: mini_fail("За дверями никого не осталось.")
                else:
                    M["trap_until"]=time.time()+1.2
                    if scream_sound: scream_sound.play()
            else:
                M["i"]+=1
                if M["i"]>=5: mini_done()
            return
def r6_update(now): pass
def r6_draw():
    if M["trap_until"]>time.time():
        screen.fill((120,0,15))
        if full_scare: screen.blit(full_scare,(0,0))
        return
    draw_text(f"ДВЕРЬ {M['i']+1} из 5. Выбери любую.",font_title,WHITE,(WIDTH//2,110))
    draw_text(f"Скримеров пережито: {M['traps_hit']}/3 (третий — смерть)",font_small,GRAY,(WIDTH//2,160))
    for d in range(3):
        rect=pygame.Rect(WIDTH//2-390+d*270,240,240,330)
        pygame.draw.rect(screen,(45,32,22),rect,border_radius=10)
        pygame.draw.rect(screen,GRAY,rect,3,border_radius=10)
        draw_text(str(d+1),font_title,WHITE,rect.center)
    # ### СЮДА МОЖНО ВСТАВИТЬ КАРТИНКУ ### — обои за дверями, например: doors_bg.png

RED_MINIS=[
{"name":"Симон говорит","start":r1_start,"handle":r1_handle,"update":r1_update,"draw":r1_draw},
{"name":"Наоборот","start":r2_start,"handle":r2_handle,"update":r2_update,"draw":r2_draw},
{"name":"Память со страхом","start":r3_start,"handle":r3_handle,"update":r3_update,"draw":r3_draw},
{"name":"Глаза в темноте","start":r4_start,"handle":r4_handle,"update":r4_update,"draw":r4_draw},
{"name":"Перевёртыш","start":r5_start,"handle":r5_handle,"update":r5_update,"draw":r5_draw},
{"name":"Три двери","start":r6_start,"handle":r6_handle,"update":r6_update,"draw":r6_draw},
]

def handle_events():
    global running,state,wire_drag,wire_errors,corner,lives,clowns_found,consecutive_dolls,box_scare_until,blood_until
    global clown_qi,anger,voice_waiting,voice_until,strip_hits,letter_index,letter_positions,word_input,letter_deadline
    global phone_li,phone_chars,roulette_turn,window_count,tablet_choice,word_feedback_until
    global clown_intro_until
    for e in pygame.event.get():
        if e.type==pygame.QUIT: running=False; continue
        if e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE: running=False; continue
        if state=="mini" and e.type in (pygame.KEYDOWN,pygame.MOUSEBUTTONDOWN,pygame.MOUSEMOTION):
            minis[mini_index]["handle"](e); continue
        if state=="word_entry" and e.type==pygame.KEYDOWN:
            if e.key==pygame.K_BACKSPACE: word_input=word_input[:-1]
            elif e.key in (pygame.K_RETURN,pygame.K_KP_ENTER):
                if word_input.strip().lower()=="клоун": state="word_success"
                else: state="word_wrong"; word_feedback_until=time.time()+2; scream_sound.play() if scream_sound else None
            elif e.unicode and e.unicode.isalpha(): word_input+=e.unicode
            continue
        if state=="strip" and e.type==pygame.KEYDOWN and e.key==pygame.K_SPACE:
            if strip_target.left<=strip_x+4<=strip_target.right:
                strip_hits+=1
                if strip_hits>=10: start_roulette()
                else: new_strip_target()
            else: miss_strip()
            continue
        if e.type==pygame.MOUSEBUTTONUP and e.button==1 and state=="wires" and wire_drag is not None:
            wire=wires[wire_drag]
            if point_near(e.pos,wire["right"]):
                wire["connected"]=True
                if all(x["connected"] for x in wires): start_hard()
            else:
                wire_errors+=1
                if wire_errors>=3: lose_attempt("Провода не удалось соединить три раза.")
            wire_drag=None; continue
        if e.type!=pygame.MOUSEBUTTONDOWN or e.button!=1: continue
        p=e.pos
        if state=="menu":
            if pygame.Rect(WIDTH//2-220,330,190,65).collidepoint(p): state="rules"
            elif pygame.Rect(WIDTH//2+30,330,190,65).collidepoint(p): running=False
        elif state=="rules" and pygame.Rect(WIDTH//2-150,500,300,60).collidepoint(p): state="confirm"
        elif state=="confirm":
            if pygame.Rect(WIDTH//2-220,365,190,65).collidepoint(p): start_easy()
            elif pygame.Rect(WIDTH//2+30,365,190,65).collidepoint(p): running=False
        elif state in ("easy","hard"):
            if corner: corner=False
            else:
                for i in range(3):
                    if pygame.Rect(WIDTH//2-270,265+i*78,540,58).collidepoint(p): answer_question(i); break
        elif state=="lost" and pygame.Rect(WIDTH//2-150,440,300,60).collidepoint(p): start_easy()
        elif state=="wires":
            wire_drag=None
            for i,w in enumerate(wires):
                if not w["connected"] and point_near(p,w["left"]): wire_drag=i; break
        elif state=="cards":
            for c in cards:
                if c["rect"].collidepoint(p) and not c["open"]:
                    c["open"]=True
                    if c["kind"]=="clown": clowns_found+=1; consecutive_dolls=0
                    else:
                        lives-=1; consecutive_dolls+=1
                        if consecutive_dolls>=2: state="box_scare"; box_scare_until=time.time()+2; scream_sound.play() if scream_sound else None
                        elif lives<=0: lose_attempt("Куклы забрали все жизни.")
                    if clowns_found>=5 and state=="cards": start_clown_talk()
                    break
        elif state=="clown_talk" and talk_done:
            for i in range(3):
                if pygame.Rect(WIDTH//2-300,450+i*62,600,50).collidepoint(p):
                    _,_,correct,medium=CLOWN_Q[clown_qi]
                    if i!=correct: anger-=10 if i==medium else 20
                    if anger<=0: lose_attempt("Клоун разозлился."); break
                    clown_qi+=1
                    if clown_qi>=len(CLOWN_Q): state="final_laugh"; laugh_until=play_for(clown_laugh,8)
                    else: voice_waiting=True; voice_until=play_for(clown_voice,random.uniform(1,3))
                    break
        elif state=="final" and final_done:
            if pygame.Rect(WIDTH//2-300,445,600,55).collidepoint(p): state="final_scare"; blood_until=time.time()+2; scream_sound.play() if scream_sound else None
            elif pygame.Rect(WIDTH//2-300,515,600,55).collidepoint(p): state="survived"
        elif state=="survived" and pygame.Rect(WIDTH//2-170,560,340,65).collidepoint(p): start_phone(["Хахаха, ты поверил?","Ты умре..."],"new_clown")
        elif state=="phone_done":
            if phone_after=="window": start_window()
            else: start_new_clown()
        elif state=="new_clown" and time.time()>=clown_intro_until and letter_positions:
            if letter_index<5:
                x,y=letter_positions[letter_index]
                if pygame.Rect(x-40,y-40,80,80).collidepoint(p):
                    letter_index+=1; letter_deadline=time.time()+2  # на букву 2 секунды
                    if letter_index>=5: state="word_entry"; word_input=""
        elif state=="word_success" and pygame.Rect(WIDTH//2-170,560,340,60).collidepoint(p): start_strip()
        elif state=="tablets":
            # Клик по самой таблетке (зоны клика считаются с учётом увеличения)
            if tablet_rects.get("red") and tablet_rects["red"].collidepoint(p): state="red_path"
            elif tablet_rects.get("blue") and tablet_rects["blue"].collidepoint(p): state="blue_path"
        elif state in ("red_path","blue_path"):
            if pygame.Rect(WIDTH//2-150,430,300,60).collidepoint(p):
                start_minis("red" if state=="red_path" else "blue")
            elif pygame.Rect(WIDTH//2-150,570,300,60).collidepoint(p): state="menu"
        elif state in ("blue_win","red_win","win") and pygame.Rect(WIDTH//2-150,570,300,60).collidepoint(p): state="menu"
        elif state=="dead" and pygame.Rect(WIDTH//2-150,440,300,60).collidepoint(p): state="menu"
        elif state=="strip_fail" and pygame.Rect(WIDTH//2-150,450,300,60).collidepoint(p): state="menu"
        elif state=="roulette" and roulette_turn=="player":
            if pygame.Rect(90,570,330,70).collidepoint(p): roulette_shot("player")
            elif pygame.Rect(680,570,330,70).collidepoint(p): roulette_shot("clown")

def update():
    global strip_x, strip_dir
    global state,wire_started,wire_errors,corner,voice_waiting,next_corner
    global phone_chars,phone_li,phone_next,window_count,window_next,dark_until,letter_positions,message,clown_intro_until
    global mini_scare_until,mini_done_until
    global letter_index,letter_deadline,talk_text,talk_shown,talk_next,talk_done
    global final_shown,final_next,final_done
    now=time.time()
    if state in ("easy","hard"):
        if now-q_started>=q_limit and not corner: lose_attempt("Время вышло.")
        elif state=="hard" and not corner and now>=next_corner: show_corner()
        elif state=="hard" and corner and now>=corner_until: lose_attempt("Она нашла тебя.")
    elif state=="wires" and now-wire_started>=5:
        wire_errors+=1
        if wire_errors>=3: lose_attempt("Провода не удалось соединить три раза.")
        else: make_wires(); wire_started=now
    elif state=="box_scare" and now>=box_scare_until:
        state="cards"
        if lives<=0: lose_attempt("Куклы забрали все жизни.")
    elif state=="clown_talk" and voice_waiting and now>=voice_until:
        voice_waiting=False
        talk_text=CLOWN_Q[clown_qi][0]; talk_shown=0; talk_next=now+0.1; talk_done=False
    elif state=="clown_talk" and not voice_waiting and not talk_done and now>=talk_next:
        if talk_shown<len(talk_text): talk_shown+=1; talk_next=now+0.06
        else: talk_done=True
    elif state=="final_laugh" and now>=laugh_until:
        state="final"; final_shown=0; final_next=now+0.3; final_done=False
    elif state=="final" and not final_done and now>=final_next:
        if final_shown<len(FINAL_Q[0]): final_shown+=1; final_next=now+0.06
        else: final_done=True
    elif state=="final_scare" and now>=blood_until: state="dead"; message="Клоун нашёл тебя."
    elif state=="strip":
        strip_x+=strip_dir*STRIP_SPEED  # полоска ускорена (было 6)
        if strip_x>=WIDTH-170 or strip_x<=170: strip_dir*=-1
        if now-strip_started>4: miss_strip()
    elif state=="strip_fail" and now>=strip_fail_until: state="dead"; message="Ты не успел."
    elif state=="roulette" and roulette_turn=="clown" and now>=roulette_next: roulette_shot(random.choice(["player","clown"]))
    elif state=="roulette_scare" and now>=roulette_next: start_phone(["А ты молодец","Не плохо держишься"],"window")
    elif state=="phone" and now>=phone_next:
        line=phone_lines[phone_li]
        if phone_chars<len(line): phone_chars+=1; phone_next=now+.11
        elif phone_li+1<len(phone_lines): phone_li+=1; phone_chars=0; phone_next=now+.5
        else:
            state="phone_done"; phone_next=now+2
            phone_music.stop()
            if phone_laugh: phone_laugh.stop()
    elif state=="phone_done" and now>=phone_next:
        if phone_after=="window": start_window()
        else: start_new_clown()
    elif state=="new_clown" and now>=clown_intro_until and not letter_positions:
        letter_positions=[(random.randint(100,WIDTH-100),random.randint(140,HEIGHT-100)) for _ in "клоун"]
        letter_deadline=now+2  # на клик по букве даётся 2 секунды
    elif state=="new_clown" and letter_positions and letter_index<5 and now>=letter_deadline:
        # Не успел за 2 секунды — скример, буквы разбегаются, счёт заново.
        if scream_sound: scream_sound.play()
        letter_positions=[(random.randint(100,WIDTH-100),random.randint(140,HEIGHT-100)) for _ in "клоун"]
        letter_index=0; letter_deadline=now+2
    elif state=="word_wrong" and now>=word_feedback_until: state="dead"; message="Неверное слово."
    elif state=="window" and now>=window_next:
        window_count+=1
        if window_count>=6: start_dark_room()
        else: window_next=now+3
    elif state=="dark_room" and now>=dark_until: state="tablets"
    elif state=="mini_scare" and now>=mini_scare_until:
        M.clear(); minis[mini_index]["start"](); state="mini"
    elif state=="mini_done" and now>=mini_done_until: next_mini()
    elif state=="mini": minis[mini_index]["update"](now)

def draw_cards():
    draw_text(
        f"Жизни: {lives}    Клоуны: {clowns_found}/5",
        font,
        WHITE,
        (WIDTH // 2, 35)
    )

    for card in cards:
        rect = card["rect"]

        # Закрытая карточка
        if not card["open"]:
            pygame.draw.rect(screen, (70, 45, 35), rect, border_radius=6)
            pygame.draw.rect(screen, GRAY, rect, 2, border_radius=6)
            draw_text("?", font_title, WHITE, rect.center)
            continue

        # Открытая карточка
        pygame.draw.rect(screen, (20, 20, 28), rect, border_radius=6)
        pygame.draw.rect(screen, WHITE, rect, 2, border_radius=6)

        if card["kind"] == "clown":
            picture = clown_card_image
        else:
            picture = doll_image

        if picture is not None:
            picture = pygame.transform.smoothscale(
                picture,
                (rect.width - 10, rect.height - 10)
            )
            picture_rect = picture.get_rect(center=rect.center)
            screen.blit(picture, picture_rect)
        else:
            print("Картинка карточки не загружена")


def draw_wires():
    draw_text("Соедини точки одинакового цвета",font_title,WHITE,(WIDTH//2,70)); draw_text(f"Время: {max(0,5-(time.time()-wire_started)):.1f}   Ошибки: {wire_errors}/3",font_small,WHITE,(WIDTH//2,125))
    for w in wires:
        pygame.draw.circle(screen,w["color"],w["left"],25); pygame.draw.circle(screen,w["color"],w["right"],25)
        if w["connected"]: pygame.draw.line(screen,w["color"],w["left"],w["right"],8)
    if wire_drag is not None: pygame.draw.line(screen,wires[wire_drag]["color"],wires[wire_drag]["left"],pygame.mouse.get_pos(),7)

def draw_clown_dialogue():
    pygame.draw.rect(screen,(70,10,20),(180,15,740,28)); pygame.draw.rect(screen,(220,35,50),(180,15,int(740*max(0,anger)/100),28)); draw_text(f"Злость: {anger}/100",font_small,WHITE,(WIDTH//2,60))
    if clown_image: screen.blit(clown_image,clown_image.get_rect(center=(WIDTH//2,245)))
    if state=="clown_talk":
        if voice_waiting: return  # звучит голос — экран молчит
        draw_text(talk_text[:talk_shown],font,WHITE,(WIDTH//2,410),600)  # вопрос печатается по буквам
        if talk_done:
            for i,a in enumerate(CLOWN_Q[clown_qi][1]): draw_button(pygame.Rect(WIDTH//2-300,450+i*62,600,50),a)
    elif state=="final_laugh": pass  # клоун смеётся — без надписи
    else:
        draw_text(FINAL_Q[0][:final_shown],font,WHITE,(WIDTH//2,410),600)  # финальный вопрос печатается по буквам
        if final_done:
            draw_button(pygame.Rect(WIDTH//2-300,445,600,55),FINAL_Q[1][0]); draw_button(pygame.Rect(WIDTH//2-300,515,600,55),FINAL_Q[1][1])

def draw_phone():
    pygame.draw.rect(screen,(25,28,35),(WIDTH//2-190,50,380,600),border_radius=35); pygame.draw.rect(screen,(130,130,140),(WIDTH//2-190,50,380,600),4,border_radius=35); pygame.draw.rect(screen,(8,10,15),(WIDTH//2-165,95,330,500),border_radius=12)
    draw_text("НЕИЗВЕСТНЫЙ НОМЕР",font_small,GRAY,(WIDTH//2,125))
    for i in range(min(phone_li+1,len(phone_lines))):
        shown=phone_lines[i][:phone_chars] if i==phone_li else phone_lines[i]
        draw_text(shown,font,WHITE,(WIDTH//2,230+i*75),300)
    if state=="phone_done": draw_text("...",font,GRAY,(WIDTH//2,430))

def draw_gun():
    """Пистолет плавно поворачивается в сторону того, в кого целятся."""
    global gun_angle
    pivot=(WIDTH//2,470); ty=350
    if roulette_spray:  # после выстрела смотрит на пострадавшего
        tx=250 if roulette_spray=="player" else WIDTH-250
    elif roulette_turn=="player":  # в свой ход следит за курсором
        mouse=pygame.mouse.get_pos()
        if pygame.Rect(90,570,330,70).collidepoint(mouse): tx=250
        elif pygame.Rect(680,570,330,70).collidepoint(mouse): tx=WIDTH-250
        else: tx=pivot[0]+1000 if ((gun_angle%360)<90 or (gun_angle%360)>270) else pivot[0]-1000
    else: tx=250  # в ход клоуна пистолет направлен на игрока
    desired=0. if tx>pivot[0] else 180.
    diff=(desired-gun_angle+180)%360-180
    gun_angle=(gun_angle+diff*0.25)%360
    if gun_image:
        img=pygame.transform.rotate(gun_image,gun_angle)
        if 90<(gun_angle%360)<270: img=pygame.transform.flip(img,False,True)
        screen.blit(img,img.get_rect(center=pivot))

def draw_roulette():
    screen.fill((22,20,25))
    for _ in range(28):
        y=random.randrange(HEIGHT); shade=random.randrange(35,95); pygame.draw.line(screen,(shade,shade,shade),(0,y),(WIDTH,y),random.randint(1,3))
    if static_image: screen.blit(static_image,(0,0),special_flags=pygame.BLEND_RGBA_MULT)
    if player_chair: screen.blit(player_chair,(130,270))
    if roulette_clown: screen.blit(roulette_clown,(WIDTH-410,230))
    draw_gun()
    draw_text(f"Игрок: {'♥ '*max(0,player_lives)}    Клоун: {'♥ '*max(0,enemy_lives)}",font,WHITE,(WIDTH//2,40)); draw_text(roulette_msg,font,WHITE,(WIDTH//2,100))
    if roulette_spray:
        x=250 if roulette_spray=="player" else WIDTH-250
        for _ in range(10): pygame.draw.circle(screen,(170,0,15),(x+random.randint(-45,45),220+random.randint(0,230)),random.randint(5,14))
    if roulette_turn=="player": draw_button(pygame.Rect(90,570,330,70),"СТРЕЛЯТЬ В СЕБЯ",RED); draw_button(pygame.Rect(680,570,330,70),"СТРЕЛЯТЬ В КЛОУНА",DARK)
    else: draw_text("Клоун выбирает цель...",font_title,RED,(WIDTH//2,600))

def draw_window():
    if forest_image: screen.blit(forest_image,(0,0))
    else: screen.fill((12,25,18)); pygame.draw.rect(screen,(55,40,25),(160,70,780,550),8)
    count=1 if window_count<2 else 2 if window_count<4 else 4; monster=window_monsters.get(count)
    if monster:
        points=[(15,140),(WIDTH-375,130),(WIDTH//2-180,85),(WIDTH//2-180,260)]
        for i in range(count): screen.blit(monster,points[(window_count+i)%len(points)])
    else: draw_text(f"Монстр заглядывает в окно ×{count}",font_title,RED,(WIDTH//2,HEIGHT//2))

def draw_tablet(name,picture,color,center):
    """Рисует одну таблетку с плавным увеличением при наведении."""
    scale=tablet_scales[name]
    size=(int(TABLET_BASE_SIZE[0]*scale),int(TABLET_BASE_SIZE[1]*scale))
    if picture is not None:
        img=pygame.transform.smoothscale(picture,size)
        screen.blit(img,img.get_rect(center=center))
    else:
        # Заглушка, если картинки нет — игра не сломается.
        pygame.draw.circle(screen,color,center,max(size)//2)
        draw_text("КРАСНАЯ" if name=="red" else "СИНЯЯ",font_small,WHITE,center)

def draw_tablets():
    update_tablets()  # плавная анимация наведения обновляется каждый кадр
    screen.fill((10,12,14))
    if forest_image: screen.blit(forest_image,(0,0))
    if room_monster: screen.blit(room_monster,room_monster.get_rect(midbottom=(WIDTH//2,650)))
    else: draw_text("МОНСТР",font_title,RED,(WIDTH//2,330))
    # Таблетки лежат на языке: красная ВЫШЕ, синяя НИЖЕ.
    draw_tablet("red",red_pill,RED,RED_TABLET_POS)
    draw_tablet("blue",blue_pill,BLUE,BLUE_TABLET_POS)
    draw_text("Выбери таблетку",font_title,WHITE,(WIDTH//2,75))

def draw_new_clown():
    if clown_final: screen.blit(clown_final,clown_final.get_rect(center=(WIDTH//2,HEIGHT//2)))
    else: draw_text("НОВЫЙ КЛОУН",font_title,WHITE,(WIDTH//2,HEIGHT//2))
    if time.time()<clown_intro_until: draw_text("БЫСТРЕЕ НАЖИМАЙ!",font_title,WHITE,(WIDTH//2,55))
    elif letter_positions and letter_index<5:
        x,y=letter_positions[letter_index]; pygame.draw.circle(screen,DARK,(x,y),45); draw_text("клоун"[letter_index],font_title,WHITE,(x,y)); draw_text(f"Буква {letter_index+1}/5",font,WHITE,(WIDTH//2,50))
        left=max(0.,letter_deadline-time.time())  # полоска времени на клик (2 секунды)
        pygame.draw.rect(screen,(60,60,80),(WIDTH//2-260,640,520,24),border_radius=6)
        pygame.draw.rect(screen,RED,(WIDTH//2-260,640,int(520*left/2),24),border_radius=6)

def draw_blood_scare():
    screen.fill((120,0,15))
    for x in range(20,WIDTH,75):
        h=random.randint(40,250); pygame.draw.rect(screen,(190,0,20),(x,0,14,h)); pygame.draw.circle(screen,(190,0,20),(x+7,h),9)
    if full_scare: screen.blit(full_scare,(0,0))

def draw_questions():
    rem=max(0,q_limit-(time.time()-q_started)); draw_text(f"Попытки: {attempts}   Время: {rem:.1f}",font_small,WHITE,(WIDTH//2,35)); draw_text(question[0],font_title,WHITE,(WIDTH//2,145),WIDTH-100)
    for i,a in enumerate(question[1]): draw_button(pygame.Rect(WIDTH//2-270,265+i*78,540,58),f"{i+1}. {a}")
    if corner:
        if corner_scare: screen.blit(corner_scare,(WIDTH-230,HEIGHT-190))
        draw_text("НАЖМИ!",font_small,WHITE,(WIDTH-120,HEIGHT-25))

def draw():
    screen.fill(BLACK)
    if state=="menu": draw_text("ПСИХОЛОГИЧЕСКИЙ ХОРРОР",font_title,WHITE,(WIDTH//2,170)); draw_text("Начать игру?",font,GRAY,(WIDTH//2,240)); draw_button(pygame.Rect(WIDTH//2-220,330,190,65),"ДА",GREEN); draw_button(pygame.Rect(WIDTH//2+30,330,190,65),"НЕТ",RED)
    elif state=="rules":
        draw_text("ПРАВИЛА ИГРЫ",font_title,WHITE,(WIDTH//2,70)); rules=["1. Действуй быстро.","2. Три попытки.","3. Чем дольше отвечаешь, тем меньше времени.","4. Если она придёт — нажимай на экран.","5. Если она нашла тебя — ты умрёшь.","6. После выбора таблетки ждут 6 испытаний."]
        for i,r in enumerate(rules): draw_text(r,font_small,WHITE,(WIDTH//2,170+i*50),WIDTH-100)
        draw_button(pygame.Rect(WIDTH//2-150,500,300,60),"ПОНЯТНО",RED)
    elif state=="confirm": draw_text("Ты уверен что хочешь играть?",font_title,WHITE,(WIDTH//2,180)); draw_button(pygame.Rect(WIDTH//2-220,365,190,65),"ДА",GREEN); draw_button(pygame.Rect(WIDTH//2+30,365,190,65),"НЕТ",RED)
    elif state in ("easy","hard"): draw_questions()
    elif state=="wires": draw_wires()
    elif state=="cards": draw_cards()
    elif state=="box_scare": screen.blit(full_scare,(0,0)) if full_scare else screen.fill(RED)
    elif state in ("clown_talk","final_laugh","final"): draw_clown_dialogue()
    elif state=="strip":
        picture=strip_clowns[min(strip_misses,2)]
        if picture: screen.blit(picture,picture.get_rect(center=(WIDTH//2,240)))
        else: draw_text("КЛОУН ОТВЕРНУЛСЯ",font_title,WHITE,(WIDTH//2,240))
        draw_text(f"Попаданий: {strip_hits}/10   Ошибок: {strip_misses}/2",font,WHITE,(WIDTH//2,470)); pygame.draw.rect(screen,(35,100,55),(160,540,780,30),border_radius=7); pygame.draw.rect(screen,(30,220,70),strip_target,border_radius=4); pygame.draw.rect(screen,WHITE,(int(strip_x),530,8,50)); draw_text("ПРОБЕЛ — нажать в зелёной зоне",font_small,WHITE,(WIDTH//2,625))
    elif state=="strip_fail": draw_text("ТЫ УМЕР : (",font_title,RED,(WIDTH//2,350)); draw_button(pygame.Rect(WIDTH//2-150,450,300,60),"В МЕНЮ")
    elif state=="roulette": draw_roulette()
    elif state=="roulette_scare": screen.blit(roulette_scare,(0,0)) if roulette_scare else (screen.blit(full_scare,(0,0)) if full_scare else screen.fill(RED))
    elif state in ("phone","phone_done"): draw_phone()
    elif state=="window": draw_window()
    elif state=="dark_room": screen.fill(BLACK)
    elif state=="tablets": draw_tablets()
    elif state=="red_path":
        draw_text("КРАСНАЯ ТАБЛЕТКА",font_title,RED,(WIDTH//2,180))
        draw_text("Путь без пощады: 6 сложных испытаний,",font,WHITE,(WIDTH//2,270))
        draw_text("путаница, глаза в темноте, много скримеров.",font,WHITE,(WIDTH//2,315))
        draw_button(pygame.Rect(WIDTH//2-150,430,300,60),"НАЧАТЬ ИСПЫТАНИЯ",RED)
        draw_button(pygame.Rect(WIDTH//2-150,570,300,60),"В МЕНЮ")
    elif state=="blue_path":
        draw_text("СИНЯЯ ТАБЛЕТКА",font_title,BLUE,(WIDTH//2,180))
        draw_text("Путь полегче: 6 простых испытаний.",font,WHITE,(WIDTH//2,270))
        draw_text("Скримеры будут, но щадящие.",font,WHITE,(WIDTH//2,315))
        draw_button(pygame.Rect(WIDTH//2-150,430,300,60),"НАЧАТЬ ИСПЫТАНИЯ",BLUE)
        draw_button(pygame.Rect(WIDTH//2-150,570,300,60),"В МЕНЮ")
    elif state=="mini": minis[mini_index]["draw"]()
    elif state=="mini_scare":
        screen.fill((120,0,15))
        if full_scare: screen.blit(full_scare,(0,0))
        draw_text("ПРОВАЛ",font_title,WHITE,(WIDTH//2,60))
    elif state=="mini_done":
        draw_text("ИСПЫТАНИЕ ПРОЙДЕНО",font_title,GREEN,(WIDTH//2,280))
        draw_text(f"Дальше: {minis[mini_index]['name']} ({mini_index+1}/6)",font,GRAY,(WIDTH//2,360))
    elif state=="blue_win":
        draw_text("СИНИЙ ПУТЬ ПРОЙДЕН",font_title,BLUE,(WIDTH//2,250))
        draw_text("Синяя таблетка была лишь иллюзией спокойствия...",font,WHITE,(WIDTH//2,340))
        draw_text("Ты выжил. Но он всё ещё где-то рядом.",font_small,GRAY,(WIDTH//2,390))
        draw_button(pygame.Rect(WIDTH//2-150,570,300,60),"В МЕНЮ")
    elif state=="red_win":
        draw_text("КРАСНЫЙ ПУТЬ ПРОЙДЕН",font_title,RED,(WIDTH//2,250))
        draw_text("Ты выдержал всё. Клоун молчит... впервые.",font,WHITE,(WIDTH//2,340))
        draw_text("Ты вырвался. Пока что.",font_small,GRAY,(WIDTH//2,390))
        draw_button(pygame.Rect(WIDTH//2-150,570,300,60),"В МЕНЮ")
    elif state in ("dead","lost"): draw_text(message if state=="lost" else "ТЫ УМЕР",font_title,RED if state=="dead" else WHITE,(WIDTH//2,200)); draw_button(pygame.Rect(WIDTH//2-150,440,300,60),"НАЧАТЬ ЗАНОВО" if state=="lost" else "В МЕНЮ")
    elif state=="survived": draw_text("ТЫ ВЫЖИЛ",font_title,GREEN,(WIDTH//2,230)); draw_button(pygame.Rect(WIDTH//2-170,560,340,65),"ПРОДОЛЖИТЬ")
    elif state=="new_clown": draw_new_clown()
    elif state=="word_entry": draw_text("Теперь введи слово из этих букв)",font_title,WHITE,(WIDTH//2,220)); pygame.draw.rect(screen,WHITE,(WIDTH//2-220,340,440,65)); draw_text(word_input,font_input,BLACK,(WIDTH//2,372)); draw_text("Набери слово и нажми Enter",font_small,GRAY,(WIDTH//2,445))
    elif state=="word_wrong": draw_blood_scare()
    elif state=="word_success": draw_text("Верно...",font_title,GREEN,(WIDTH//2,250)); draw_button(pygame.Rect(WIDTH//2-170,560,340,60),"ДАЛЬШЕ")

def main():
    global running
    while running:
        handle_events(); update()
        draw(); pygame.display.flip(); clock.tick(60)
    pygame.quit(); sys.exit()

if __name__=="__main__": main()
