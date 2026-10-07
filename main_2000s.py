import tkinter as tk
import tkinter.font as tkfont
import random
import cv2
import os
import webbrowser
import requests
import queue
import hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

from PIL import Image, ImageTk, ImageDraw, ImageEnhance, ImageFilter
from deepface import DeepFace
from dotenv import load_dotenv
from supabase import create_client


# ============================================================
# NIGHT FURRY — 2000s SCRAPBOOK / BRATZ-ISH EDITION
# ============================================================
# Functional flow stays the same:
# camera -> saved frame -> DeepFace -> emotion -> vibe -> songs -> Spotify
# Presentation is the only thing being redesigned here.
# ============================================================

# -----------------------------
# Palette: lived-in 2000s scrapbook
# -----------------------------
BG = "#24182E"
BG_BLUE = "#78B9E8"
PINK = "#F26AAE"
HOT_PINK = "#C92D72"
LILAC = "#9C78D4"
MINT = "#91C9A0"
BUTTER = "#FFD36E"
CREAM = "#FFF0F3"
PAPER = "#FFFDFC"
PAPER_2 = "#F7F0FA"
INK = "#241A20"
INK_SOFT = "#6B5668"
BORDER = "#8D5573"
STICKER_PINK = "#F7C8E0"
STICKER_BLUE = "#AEE8E8"
STICKER_LILAC = "#C9A7FF"
STICKER_YELLOW = "#FFD98E"
STICKER_GREEN = "#B8E986"
WHITE = "#FFFFFF"

# -----------------------------
# Backend / music library
# -----------------------------
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_songs_by_vibe(vibe, limit=1000):
    """Fetch the full set of songs for the selected vibe.

    The project currently contains about 530 songs, so a 1000-row cap
    keeps the whole library available without truncating the user's work.
    """
    if supabase is None:
        raise RuntimeError("Music library is not configured.")

    response = (
        supabase
        .table("songs")
        .select("title,artist,spotify_url,cover_url")
        .eq("vibe", vibe.lower())
        .limit(int(limit))
        .execute()
    )
    return response.data or []


def open_spotify(url):
    if url:
        try:
            webbrowser.open_new_tab(url)
        except Exception:
            pass


# -----------------------------
# Tk root first, THEN font probing
# -----------------------------
window = tk.Tk()
window.title("night furry — mood mail / 2006")
window.configure(bg=BG)
try:
    window.state("zoomed")
except tk.TclError:
    window.geometry("1280x800")
window.minsize(1100, 760)
window.update_idletasks()

AVAILABLE_FONTS = set(tkfont.families(window))


def pick_font(options):
    for name in options:
        if name in AVAILABLE_FONTS:
            return name
    return "Arial"


TITLE_FACE = pick_font([
    "Cooper Black",
    "Baskerville",
    "Georgia",
    "Arial Rounded MT Bold",
    "Trebuchet MS",
    "Arial",
])
BODY_FACE = pick_font([
    "Tahoma",
    "Verdana",
    "Arial",
])
HAND_FACE = pick_font([
    "Segoe Print",
    "Segoe Script",
    "Comic Sans MS",
    "Trebuchet MS",
])

TITLE = (TITLE_FACE, 32, "bold")
TITLE_SMALL = (TITLE_FACE, 19, "bold")
HEAD = (TITLE_FACE, 23, "bold")
BODY = (BODY_FACE, 11)
BODY_BOLD = (BODY_FACE, 10, "bold")
HAND = (HAND_FACE, 10, "bold")
HAND_BIG = (HAND_FACE, 14, "bold")
SMALL = (BODY_FACE, 8)

# ============================================================
# THE LITTLE INTERNET CORNER — colourful, lived-in, not a template
# ============================================================
def make_wallpaper(width, height):
    width = max(int(width), 1200)
    height = max(int(height), 800)
    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)

    # Colourful early-internet wall: no brown/mustard wash.
    draw.rectangle([0, 0, width, height], fill=BG)
    draw.rectangle([0, 0, width, 92], fill="#372044")
    draw.rectangle([0, height - 88, width, height], fill="#1C1324")

    # Crooked colour fields, like bits of old posters/paper left behind.
    draw.polygon([(36, 120), (250, 84), (315, 262), (202, 330), (42, 282)], fill="#E85D9A")
    draw.polygon([(width-315, 92), (width-60, 128), (width-92, 292), (width-350, 242)], fill="#7C57B2")
    draw.polygon([(60, height-270), (244, height-306), (318, height-118), (92, height-94)], fill="#65BFC4")
    draw.polygon([(width-330, height-272), (width-84, height-318), (width-42, height-102), (width-300, height-74)], fill="#92C96F")
    draw.ellipse([width//2-125, 34, width//2+130, 188], fill="#FFD36E")
    draw.ellipse([width//2-68, 72, width//2+64, 150], fill="#F38AB7")

    # Early-web style pixel confetti.
    pixels = ["#FF5FA2", "#7FE3DE", "#B991FF", "#FFD66F", "#A9E87B", "#F05C66", "#86AEEB"]
    for _ in range(180):
        x = random.randrange(width)
        y = random.randrange(height)
        s = random.choice([2, 2, 3, 4])
        draw.rectangle([x, y, x+s, y+s], fill=random.choice(pixels))

    # Tiny stars / flower doodles.
    for x, y, c in [(110, 58, "#FFD66F"), (370, 70, "#7FE3DE"), (width-160, 62, "#FF5FA2"), (width-270, height-48, "#B991FF")]:
        draw.line((x-8, y, x+8, y), fill=c, width=2)
        draw.line((x, y-8, x, y+8), fill=c, width=2)
        draw.ellipse([x-3, y-3, x+3, y+3], fill=c)

    # Light film grain.
    noise = Image.effect_noise((width, height), 16).convert("L")
    grain = Image.merge("RGB", (noise, noise, noise))
    img = Image.blend(img, grain, 0.035)
    return ImageTk.PhotoImage(img)

wallpaper_img = make_wallpaper(window.winfo_screenwidth(), window.winfo_screenheight())
wallpaper = tk.Label(window, image=wallpaper_img, bd=0, highlightthickness=0)
wallpaper.place(relx=0, rely=0, relwidth=1, relheight=1)
wallpaper.lower()

# A slightly imperfect central page — the place itself is the interface.
shadow = tk.Frame(window, bg="#160F1D", bd=0)
shadow.place(relx=0.505, rely=0.51, anchor="center", relwidth=0.86, relheight=0.89)
board = tk.Frame(window, bg=CREAM, highlightthickness=2, highlightbackground="#6D3553")
board.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.86, relheight=0.89)
board.lift()

titlebar = tk.Frame(board, bg="#24182E", height=34)
titlebar.pack(fill="x")
titlebar.pack_propagate(False)
tk.Label(titlebar, text="✦", bg="#24182E", fg="#FFD36E", font=HAND_BIG).pack(side="left", padx=9)
tk.Label(titlebar, text="night furry / open late", bg="#24182E", fg="#F7C8E0", font=BODY_BOLD).pack(side="left")
tk.Label(titlebar, text="somewhere on the old internet ♡", bg="#24182E", fg="#AEE8E8", font=HAND).pack(side="right", padx=13)

nav = tk.Frame(board, bg="#F7D5E2", height=38, highlightthickness=1, highlightbackground="#B85E84")
nav.pack(fill="x", padx=12, pady=(8, 0))
nav.pack_propagate(False)
content = tk.Frame(board, bg=CREAM)
content.pack(fill="both", expand=True, padx=12, pady=9)

# ============================================================
# SCREEN MANAGEMENT
# ============================================================
home_frame = tk.Frame(content, bg=CREAM)
camera_frame = tk.Frame(content, bg=CREAM)
vibe_frame = tk.Frame(content, bg=CREAM)
results_frame = tk.Frame(content, bg=CREAM)
ALL_SCREENS = (home_frame, camera_frame, vibe_frame, results_frame)


def show_screen(frame):
    for screen in ALL_SCREENS:
        screen.pack_forget()
    frame.pack(fill="both", expand=True)


# ============================================================
# ROTATING HUMAN GOSSIP / FACTS
# ============================================================

ROTATING_POOLS = {
    "gossip": [
        "okay, important: this is giving the song you play on the bus ride home and stare out the window for no reason.",
        "tiny update from the universe: your headphones have been carrying this whole personality department.",
        "this has the exact energy of finding one song at 1:12 a.m. and suddenly needing it on repeat for three days.",
        "you know that one song you would NEVER skip, even after hearing the first two seconds? yeah. we're looking for its cousin.",
        "the mood is a little too specific today. honestly? good. specific people deserve specific playlists.",
        "this feels like a burnt-CD situation. twelve songs, one extremely serious emotional commitment.",
        "somebody put the Nokia on silent. we're having a soundtrack moment.",
        "your current vibe would absolutely have had an MSN status. i'm just saying.",
        "this is less random shuffle and more the movie scene where everything suddenly looks prettier.",
        "you have the face of someone who would save a song to a secret folder and never explain why.",
        "the music shelf has been informed that you are not accepting boring today.",
        "there is a suspicious amount of main-character energy in this room.",
        "this is giving 2006 digital-camera flash, low-resolution photos, and one song that makes everything cinematic.",
        "your mood has entered its 'let me stare at the ceiling and think about everything' era.",
        "not to make allegations, but your playlist probably has one song that reminds you of a very specific person.",
        "the committee has reviewed your face. the committee says: one more song.",
        "this is the part where the opening credits would start.",
        "honestly? the right song could make an ordinary Tuesday feel like a memory.",
        "very Gossip Girl hallway energy. unfortunately, the headphones are involved now.",
        "this needs the kind of song people used to put on a MySpace page and never change.",
    ],
    "facts": [
        "MSN had status messages. yours would probably change three times before the song finished.",
        "burned CDs were basically physical playlists: people used to make one and hand it to someone like it meant something.",
        "digital cameras made everybody a little photographer because 37 blurry pictures was apparently the correct number.",
        "Orkut scraps, MSN nudges and profile songs were early ways of saying 'this reminded me of you' without saying it.",
        "the iPod made carrying hundreds of songs around feel futuristic. somehow we still miss that little white box.",
        "album art used to be part of the experience: a tiny square you stared at while reading the CD booklet.",
        "ringtone culture was serious business. picking one felt like choosing an outfit for your phone.",
        "the 2000s internet was full of glitter buttons, custom backgrounds, profile music and pages that looked unmistakably like their owner.",
        "a playlist can change the way a memory feels because music gets tied to places, people and moments.",
        "sometimes the song you need isn't the song that matches the emotion. it is the one that knows where to take it next.",
        "That's So Raven logic says the face knows something. our logic says you still get the final say.",
        "Lizzie McGuire era rule: an outfit, a song and the right mood could make a completely normal day feel iconic.",
        "Bratz understood the assignment early: the vibe was always part of the personality.",
        "High School Musical gave an entire generation a soundtrack for approximately every possible feeling.",
    ],
    "vibe": [
        "this choice is very 'one song on repeat while the whole room turns into a movie scene.'",
        "you picked this like someone who already knows exactly what kind of evening this is.",
        "okayyy, this is giving a very specific 2000s montage. i approve.",
        "this is the soundtrack equivalent of opening the old camera roll at midnight.",
        "there is definitely a scene in your life that this playlist is trying to score.",
        "the obvious choice would have been boring. this one has better taste.",
        "i'm getting headphones-on, world-off energy from this decision.",
        "this mood deserves songs with a little personality, not background noise.",
        "this feels like the bit before the camera cuts to the song title.",
    ],
}

EMOTION_GOSSIP = {
    "sad": [
        "okay. no fixing the whole world tonight. let's just find one song that sits with you properly.",
        "this is giving 2 a.m. window stare, old playlists, and suddenly understanding a lyric way too well.",
        "your face says 'i need a song, not a lecture.' understood.",
        "we are not forcing a happy mood. we're finding the song that makes this one feel a little less lonely.",
        "this is absolutely a 'play the song all the way through and don't touch anything' kind of moment.",
        "very One Tree Hill bedroom-window energy. let the playlist be dramatic for a minute.",
    ],
    "angry": [
        "oh. somebody has entered their 'do not test me' era.",
        "your face is basically saying the soundtrack better keep up.",
        "this is giving the scene where the main character walks away before saying something unforgivable.",
        "we can scream, cool down, or go full movie montage. your call.",
        "the playlist has been warned. it has approximately one chance to get this right.",
        "this is not the time for a weak chorus. be serious.",
    ],
    "happy": [
        "wait, keep this one. this is the kind of mood people try to remember later.",
        "your face is doing the whole 'everything suddenly feels possible' thing.",
        "this is dangerously close to a summer-movie montage.",
        "honestly? this mood deserves a soundtrack with zero skips.",
        "someone get the digital camera. this one needs documenting.",
        "this is giving the episode ending where everyone is suddenly outside and the music is perfect.",
    ],
    "neutral": [
        "your face has chosen mystery. extremely early-internet of you.",
        "neutral, but not boring. more like the quiet scene before something happens.",
        "this is giving headphones on, wandering around, accidentally finding a new favourite song.",
        "your face says 'surprise me' before you've even picked a button.",
        "the mood is unreadable. perfect. those are usually the fun playlists.",
    ],
    "fear": [
        "okay, we're choosing comfort first. nobody needs a soundtrack that makes this worse.",
        "your face says 'gentle, please.' message received.",
        "this is a soft-blanket, low-volume, one-good-song kind of moment.",
        "no dramatic soundtrack required. just something that lets your shoulders drop a little.",
        "we're not rushing this. the right song can make a room feel different.",
    ],
    "surprise": [
        "well. something clearly happened. the face has submitted the evidence.",
        "this is giving the scene right before the plot changes.",
        "your face has absolutely no explanation and honestly? i respect that.",
        "something unexpected just walked into the storyline. soundtrack accordingly.",
        "this is prime 'put one weirdly perfect song on and see what happens' territory.",
    ],
    "disgust": [
        "yeah, no. whatever that was, we're cleansing the playlist immediately.",
        "your face has filed a formal complaint against the current energy.",
        "this is giving 'skip. SKIP. next song.'",
        "we've seen enough. time to put something with taste back on.",
        "the soundtrack has been granted permission to start over.",
    ],
}
ROTATING_QUEUES = {}


def rotate_text(pool):
    q = ROTATING_QUEUES.get(pool, [])
    if not q:
        q = list(range(len(ROTATING_POOLS[pool])))
        random.shuffle(q)
    idx = q.pop()
    ROTATING_QUEUES[pool] = q
    return ROTATING_POOLS[pool][idx]

def rotate_emotion_gossip(emotion):
    options = EMOTION_GOSSIP.get(emotion, EMOTION_GOSSIP["neutral"])
    key = f"emotion:{emotion}"
    q = ROTATING_QUEUES.get(key, [])
    if not q:
        q = list(range(len(options)))
        random.shuffle(q)
    idx = q.pop()
    ROTATING_QUEUES[key] = q
    return options[idx]


# ============================================================
# UI HELPERS
# ============================================================
def sticker(parent, text, bg_color, fg=INK, command=None, font=HAND, padx=11, pady=5):
    outer = tk.Frame(parent, bg="#6A4A4A", padx=1, pady=1)
    inner = tk.Label(
        outer,
        text=text,
        bg=bg_color,
        fg=fg,
        font=font,
        padx=padx,
        pady=pady,
        cursor="hand2" if command else "",
        justify="center",
    )
    inner.pack()
    if command:
        inner.bind("<Button-1>", lambda e: command())
    inner.bind("<Enter>", lambda e: inner.configure(relief="raised", bd=1))
    inner.bind("<Leave>", lambda e: inner.configure(relief="flat", bd=0))
    return outer


def paper_label(parent, text, font=BODY, fg=INK, bg=PAPER, **kwargs):
    return tk.Label(parent, text=text, font=font, fg=fg, bg=bg, **kwargs)


def separator(parent):
    tk.Frame(parent, bg="#B99F91", height=1).pack(fill="x", pady=6)


def tape(parent, text="tape"):
    label = tk.Label(parent, text=text, bg="#E6C98F", fg="#6E5840", font=SMALL, padx=12, pady=2)
    return label


def small_rule(parent, colour="#CBB1A3"):
    return tk.Frame(parent, bg=colour, height=1)

# ============================================================
# REAL FUNCTIONAL STICKERS
# ============================================================
last_emotion = "neutral"
current_songs = []
current_vibe = ""


def open_captured_photo():
    path = Path("captured_face.jpg").resolve()
    if path.exists():
        try:
            os.startfile(str(path))
        except Exception:
            webbrowser.open(path.as_uri())
    else:
        popup("my snap ♡", "no snap yet — take your first mood photo and it'll live here.")


def show_mood_note():
    mood = last_emotion.upper() if last_emotion else "WAITING"
    vibe = current_vibe or "nothing chosen yet"
    popup("mood diary", f"today's face says: {mood}\n\nlatest vibe: {vibe}\n\nno judgement. just a soundtrack.")


def show_gossip_popup():
    popup("xoxo gossip", rotate_text("gossip"))


def show_current_music():
    if current_songs:
        show_results(current_songs, current_vibe)
    else:
        popup("my music shelf", "your shelf is empty for now ♡\nread my face and pick a vibe first.")


def popup(title, message):
    win = tk.Toplevel(window)
    win.title(title)
    win.geometry("420x270")
    win.configure(bg=PAPER)
    win.transient(window)
    win.resizable(False, False)

    bar = tk.Frame(win, bg=PINK, height=32)
    bar.pack(fill="x")
    bar.pack_propagate(False)
    tk.Label(bar, text=f"♡ {title}", bg=PINK, fg=INK, font=BODY_BOLD).pack(side="left", padx=10)

    body = tk.Frame(win, bg=PAPER, padx=20, pady=20)
    body.pack(fill="both", expand=True)
    tk.Label(body, text=message, bg=PAPER, fg=INK, font=BODY, justify="left", wraplength=360).pack(fill="both", expand=True)
    tk.Button(
        body, text="okie bye ♡", command=win.destroy,
        bg=STICKER_YELLOW, fg=INK, relief="groove", bd=1,
        font=BODY_BOLD, cursor="hand2", padx=12, pady=5
    ).pack(anchor="e")


# ============================================================
# WORLD OBJECT HELPERS — physical-ish without becoming clutter
# ============================================================
def world_object(parent, text, bg, fg=INK, command=None, font=HAND, padx=10, pady=5, angle=""):
    outer = tk.Frame(parent, bg="#2D1C34", padx=1, pady=1)
    inner = tk.Label(outer, text=text, bg=bg, fg=fg, font=font, padx=padx, pady=pady, cursor="hand2" if command else "", justify="left")
    inner.pack()
    if command:
        inner.bind("<Button-1>", lambda e: command())
        inner.bind("<Enter>", lambda e: inner.configure(bg=WHITE))
        inner.bind("<Leave>", lambda e: inner.configure(bg=bg))
    return outer

def tiny_tape(parent, bg="#FFFFFF", width=70):
    tape_frame = tk.Frame(parent, bg=bg, width=width, height=12)
    tape_frame.pack_propagate(False)
    tape_frame.configure(highlightthickness=1, highlightbackground="#C6B8C6")
    return tape_frame

def page_number(parent, text):
    tk.Label(parent, text=text, bg=CREAM, fg=INK_SOFT, font=("Tahoma", 8)).pack(anchor="e", padx=6, pady=2)

# ============================================================
# HOME — a small digital world, not a landing page
# ============================================================
show_screen(home_frame)
opening_lines = [
    "can't sleep? maybe tonight just needs better music.",
    "okay. tell me everything. we'll start with a song.",
    "2 a.m. is a very specific kind of mood.",
    "some nights are easier with headphones.",
    "today's soundtrack starts somewhere around here.",
    "stay for a minute. see what you find.",
]

now_label = __import__('datetime').datetime.now().strftime("%a %d %b  ·  %I:%M %p")

home_top = tk.Frame(home_frame, bg=CREAM, height=30)
home_top.pack(fill="x")
home_top.pack_propagate(False)
tk.Label(home_top, text="private page / don't make it weird", bg=CREAM, fg=HOT_PINK, font=TITLE_SMALL).pack(side="left")
tk.Label(home_top, text=now_label.lower(), bg=CREAM, fg=INK_SOFT, font=SMALL).pack(side="right", pady=6)
small_rule(home_frame).pack(fill="x", pady=(2, 6))

home_body = tk.Frame(home_frame, bg=CREAM)
home_body.pack(fill="both", expand=True)

# LEFT: a colourful pile of things someone might actually keep.
left = tk.Frame(home_body, bg=CREAM, width=330)
left.pack(side="left", fill="y", padx=(2, 12))
left.pack_propagate(False)

# Magazine clipping.
mag = tk.Frame(left, bg="#F7C8E0", highlightthickness=1, highlightbackground="#A64B74", padx=12, pady=10)
mag.place(x=18, y=12, width=238, height=126)
tiny_tape(mag).place(x=74, y=-6)
tk.Label(mag, text="THE NIGHT ISSUE", bg="#F7C8E0", fg="#7F254D", font=(TITLE_FACE, 11, "bold")).pack(anchor="w")
tk.Label(mag, text="things girls do after midnight", bg="#F7C8E0", fg=INK, font=(TITLE_FACE, 16, "bold"), justify="left", wraplength=200).pack(anchor="w", pady=(4, 0))
tk.Label(mag, text="music / secrets / terrible decisions", bg="#F7C8E0", fg="#7F254D", font=HAND).pack(anchor="w", pady=(5, 0))

# Digital camera object -> real photo function.
cam_obj = tk.Frame(left, bg="#BFEAF0", highlightthickness=2, highlightbackground="#39777C", padx=10, pady=10)
cam_obj.place(x=64, y=115, width=238, height=214)
tiny_tape(cam_obj, bg="#DDEFF1").place(x=82, y=-6)
tk.Label(cam_obj, text="DIGITAL CAMERA", bg="#BFEAF0", fg="#2D5B62", font=BODY_BOLD).pack(anchor="w")
cam_canvas = tk.Canvas(cam_obj, bg="#607277", width=178, height=108, highlightthickness=2, highlightbackground="#284145")
cam_canvas.pack(pady=(8, 6))
cam_canvas.create_rectangle(14, 13, 166, 95, fill="#25202D", outline="#EAE4F0", width=2)
cam_canvas.create_oval(65, 27, 115, 77, outline="#DAD3E2", width=3)
cam_canvas.create_oval(83, 45, 97, 59, fill="#88D9DA", outline="")
cam_canvas.create_rectangle(22, 18, 46, 26, fill="#F7C8E0", outline="")
cam_canvas.bind("<Button-1>", lambda e: open_camera())
tk.Label(cam_obj, text="take a stupid little picture →", bg="#BFEAF0", fg="#2D5B62", font=HAND, cursor="hand2").pack(anchor="w")
cam_obj.bind("<Button-1>", lambda e: open_camera())

# CD with real music action.
cd_obj = tk.Frame(left, bg="#B9A0F1", highlightthickness=1, highlightbackground="#6C4F9B", padx=10, pady=8)
cd_obj.place(x=2, y=318, width=205, height=112)
tk.Canvas(cd_obj, bg="#B9A0F1", highlightthickness=0, width=62, height=62).pack(side="left")
# draw CD using the canvas returned above via searching last child
cd_cv = cd_obj.winfo_children()[0]
cd_cv.create_oval(5,5,57,57, fill="#DDE3F4", outline="#6A6580")
cd_cv.create_oval(21,21,41,41, fill="#B9A0F1", outline="#6A6580")
cd_cv.create_oval(29,29,35,35, fill="#E94B5B", outline="")
cd_cv.bind("<Button-1>", lambda e: show_current_music())
tk.Label(cd_obj, text="SIDE A", bg="#B9A0F1", fg="#503A7A", font=BODY_BOLD).pack(anchor="w")
tk.Label(cd_obj, text="songs i kept\nfor a reason", bg="#B9A0F1", fg=INK, font=HAND, justify="left").pack(anchor="w")

# Hidden-ish note, but clickable.
secret = world_object(left, "don't unfold this yet", "#FFD36E", fg="#6E4C1A", command=show_gossip_popup, font=HAND, padx=9, pady=7)
secret.place(x=112, y=425)

# MAIN: actual diary page.
diary = tk.Frame(home_body, bg=PAPER, highlightthickness=2, highlightbackground="#B45A7B", padx=25, pady=18)
diary.pack(side="left", fill="both", expand=True, pady=(0, 4))

# little paper corners
tk.Label(diary, text="♡", bg=PAPER, fg="#F05E9D", font=HAND_BIG).place(relx=.96, rely=.02)
tk.Label(diary, text="✦", bg=PAPER, fg="#8D78C8", font=HAND_BIG).place(relx=.88, rely=.87)

tk.Label(diary, text="12:17 AM / PAGE 01", bg=PAPER, fg=HOT_PINK, font=BODY_BOLD).pack(anchor="w")
opening_note = tk.Label(diary, text=random.choice(opening_lines), bg=PAPER, fg=INK, font=(TITLE_FACE, 28, "bold"), justify="left", wraplength=640)
opening_note.pack(anchor="w", pady=(7, 2))
tk.Label(diary, text="a tiny corner of the internet for when you don't really know what you need.", bg=PAPER, fg=INK_SOFT, font=BODY, justify="left", wraplength=580).pack(anchor="w")

# Handwritten thought overlaps the page edge visually.
thought = tk.Frame(diary, bg="#AEE8E8", highlightthickness=1, highlightbackground="#4A8F92", padx=14, pady=11)
thought.pack(fill="x", pady=(16, 12), padx=(12, 42))
tiny_tape(thought).place(x=68, y=-6)
tk.Label(thought, text="written in the margin", bg="#AEE8E8", fg="#3E696B", font=HAND).pack(anchor="w")
tk.Label(thought, text="sometimes the right song is the one\nthat gives the feeling somewhere to go.", bg="#AEE8E8", fg="#234A4C", font=HAND_BIG, justify="left").pack(anchor="w", pady=(4,0))

# THE ENTRY — obvious route to actual working camera.
entry_row = tk.Frame(diary, bg=PAPER)
entry_row.pack(fill="x", pady=(5, 0))
start_btn = tk.Button(entry_row, text="SHOW ME  ♡", command=lambda: open_camera(), bg=HOT_PINK, fg=WHITE, activebackground="#A51E59", activeforeground=WHITE, font=(TITLE_FACE, 14, "bold"), relief="raised", bd=2, cursor="hand2", padx=23, pady=10)
start_btn.pack(side="left")
start_btn.bind("<ButtonPress-1>", lambda e: start_btn.configure(relief="sunken", bd=1))
start_btn.bind("<ButtonRelease-1>", lambda e: start_btn.configure(relief="raised", bd=2))
tk.Label(entry_row, text="↑ this is the door", bg=PAPER, fg=INK_SOFT, font=HAND).pack(side="left", padx=10)

# Three objects at the bottom, each an actual existing action.
objects = tk.Frame(diary, bg=PAPER)
objects.pack(fill="x", side="bottom", pady=(14, 0))
for label, copy, color, cmd in [
    ("PHOTO ROLL", "your last little snap", "#FFD98E", open_captured_photo),
    ("MOOD NOTE", "what the face said", "#B8E986", show_mood_note),
    ("MUSIC DRAWER", "songs waiting inside", "#C9A7FF", show_current_music),
]:
    obj = world_object(objects, f"{label}\n{copy}", color, fg=INK, command=cmd, font=HAND, padx=10, pady=7)
    obj.pack(side="left", padx=4)

tk.Label(diary, text="some things on this page aren't labelled. that's the point.", bg=PAPER, fg="#A05D7E", font=HAND).pack(anchor="e", pady=(7,0))
page_number(home_frame, "01")

# ============================================================
# CAMERA — old mall photobooth energy
# ============================================================
cam_top = tk.Frame(camera_frame, bg=CREAM, height=30)
cam_top.pack(fill="x")
cam_top.pack_propagate(False)
tk.Label(cam_top, text="PHOTOBOOTH / 2006", bg=CREAM, fg=HOT_PINK, font=HEAD).pack(side="left")
tk.Label(cam_top, text="one frame. keep it.", bg=CREAM, fg=INK_SOFT, font=HAND).pack(side="right", pady=6)

cam_layout = tk.Frame(camera_frame, bg=CREAM)
cam_layout.pack(fill="both", expand=True, pady=(5, 0))
cam_layout.grid_columnconfigure(0, weight=6)
cam_layout.grid_columnconfigure(1, weight=2)
cam_layout.grid_rowconfigure(0, weight=1)

# Booth frame: colourful object, not a generic webcam rectangle.
cam_booth_shadow = tk.Frame(cam_layout, bg="#381D31", padx=6, pady=6)
cam_booth_shadow.grid(row=0, column=0, sticky="nsew", padx=(0,14))
cam_booth = tk.Frame(cam_booth_shadow, bg="#F7C8E0", highlightthickness=3, highlightbackground="#7B2F52", padx=14, pady=14)
cam_booth.pack(fill="both", expand=True)

tk.Label(cam_booth, text="♡ MALL PHOTO BOOTH ♡", bg="#F7C8E0", fg="#7B2F52", font=(TITLE_FACE, 14, "bold")).pack(anchor="w")
window_label = tk.Label(cam_booth, text="FLASH\nMEMORY\nLOADING...", bg="#202030", fg="#F4EDF5", font=(TITLE_FACE, 16, "bold"), justify="center")
window_label.pack(anchor="e", pady=(0, 5))

photo_window = tk.Frame(cam_booth, bg="#201C29", highlightthickness=3, highlightbackground="#91DADC", padx=5, pady=5)
photo_window.pack(fill="both", expand=True, pady=(3, 10))
camera_label = tk.Label(photo_window, bg="#2B2635", text="")
camera_label.pack(fill="both", expand=True)

# Little booth control strip.
cam_controls = tk.Frame(cam_booth, bg="#F7C8E0")
cam_controls.pack(fill="x")
take_btn = tk.Button(cam_controls, text="FLASH / TAKE PHOTO", command=lambda: capture_photo(), bg="#D62F75", fg=WHITE, activebackground="#A91D59", activeforeground=WHITE, font=(TITLE_FACE, 11, "bold"), relief="raised", bd=2, cursor="hand2", padx=16, pady=8)
take_btn.pack(side="left")
take_btn.bind("<ButtonPress-1>", lambda e: take_btn.configure(relief="sunken", bd=1))
take_btn.bind("<ButtonRelease-1>", lambda e: take_btn.configure(relief="raised", bd=2))
tk.Button(cam_controls, text="← leave the booth", command=lambda: cancel_camera(), bg="#AEE8E8", fg=INK, relief="raised", bd=1, font=BODY_BOLD, cursor="hand2", padx=11, pady=7).pack(side="left", padx=8)
tk.Label(cam_controls, text="SPACE snaps it  ·  Q backs out", bg="#F7C8E0", fg="#7B4B61", font=SMALL).pack(side="right", padx=3)

# Side pile: memories rather than instructions.
cam_side = tk.Frame(cam_layout, bg=CREAM, width=235)
cam_side.grid(row=0, column=1, sticky="nsew")
cam_side.grid_propagate(False)

note1 = tk.Frame(cam_side, bg="#FFD36E", highlightthickness=1, highlightbackground="#AE8528", padx=13, pady=12)
note1.pack(fill="x")
tiny_tape(note1, bg="#FFF7D9").place(x=48, y=-6)
tk.Label(note1, text="MUSIC GOSSIP", bg="#FFD36E", fg="#6B4B15", font=BODY_BOLD).pack(anchor="w")
camera_gossip_label = tk.Label(note1, text=rotate_text("gossip"), bg="#FFD36E", fg="#4A3719", font=HAND, justify="left", wraplength=205)
camera_gossip_label.pack(anchor="w", pady=(7,0))

note2 = tk.Frame(cam_side, bg="#AEE8E8", highlightthickness=1, highlightbackground="#5A9494", padx=13, pady=12)
note2.pack(fill="x", pady=12)
tk.Label(note2, text="SOMETHING I REMEMBER", bg="#AEE8E8", fg="#3D696B", font=BODY_BOLD).pack(anchor="w")
camera_fact_label = tk.Label(note2, text=rotate_text("facts"), bg="#AEE8E8", fg="#254B4C", font=BODY, justify="left", wraplength=205)
camera_fact_label.pack(anchor="w", pady=(7,0))

# Physical-strip motif (visual only).
strip = tk.Frame(cam_side, bg="#FFFFFF", highlightthickness=1, highlightbackground="#C1B9C8", padx=6, pady=6)
strip.pack(anchor="w", pady=(3, 0), padx=18)
for i, cap in enumerate(["click", "flash", "keep this"]):
    cell = tk.Frame(strip, bg=["#87B8E6", "#F178AE", "#B4E77C"][i], width=134, height=56)
    cell.pack(pady=3)
    cell.pack_propagate(False)
    tk.Label(cell, text=cap, bg=cell.cget("bg"), fg=INK, font=HAND).pack(anchor="sw", padx=6, pady=4)

world_object(cam_side, "your face stays\nexactly the same for\nthe emotion check.", "#C9A7FF", fg="#46305F", font=HAND, padx=10, pady=8).pack(anchor="w", pady=9, padx=3)

# ============================================================
# VIBE PAGE — colour personalities hanging out together
# ============================================================
tk.Label(vibe_frame, text="HOW ARE WE FEELING TONIGHT?", bg=CREAM, fg=HOT_PINK, font=HEAD).pack(anchor="w")
tk.Label(vibe_frame, text="your face started the conversation. you get to choose what it means.", bg=CREAM, fg=INK_SOFT, font=BODY).pack(anchor="w", pady=(0, 5))

vibe_header = tk.Frame(vibe_frame, bg="#24182E", highlightthickness=2, highlightbackground="#7B3555", padx=18, pady=11)
vibe_header.pack(fill="x", pady=(1, 9))
tk.Label(vibe_header, text="FACE CHECK /", bg="#24182E", fg="#F7C8E0", font=BODY_BOLD).pack(side="left")
emotion_label = tk.Label(vibe_header, text="WAITING", bg="#24182E", fg="#FFD36E", font=TITLE_SMALL)
emotion_label.pack(side="left", padx=7)
vibe_gossip_label = tk.Label(vibe_header, text=rotate_text("vibe"), bg="#24182E", fg="#AEE8E8", font=HAND, wraplength=470, justify="left")
vibe_gossip_label.pack(side="right", padx=8)
message_label = tk.Label(vibe_frame, text="", bg=CREAM, fg=INK_SOFT, font=HAND, justify="left")
message_label.pack(anchor="w", pady=(0, 7))

vibe_stage = tk.Frame(vibe_frame, bg=CREAM)
vibe_stage.pack(fill="both", expand=True)
vibe_stage.grid_columnconfigure(0, weight=2)
vibe_stage.grid_columnconfigure(1, weight=5)
vibe_stage.grid_rowconfigure(0, weight=1)

# A little diary margin.
emotion_card = tk.Frame(vibe_stage, bg="#F1D7E3", highlightthickness=2, highlightbackground="#8A4263", padx=17, pady=16, width=220)
emotion_card.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
emotion_card.grid_propagate(False)
tk.Label(emotion_card, text="TODAY'S LITTLE CLUE", bg="#F1D7E3", fg="#8A4263", font=BODY_BOLD).pack(anchor="w")
emotion_big = tk.Label(emotion_card, text="NEUTRAL", bg="#F1D7E3", fg=INK, font=(TITLE_FACE, 28, "bold"), wraplength=178, justify="left")
emotion_big.pack(anchor="w", pady=(11, 12))
world_object(emotion_card, "the camera\ngets a clue.\nyou write the story.", "#AEE8E8", fg="#2F5C5F", font=HAND, padx=8, pady=7).pack(anchor="w")
tk.Label(emotion_card, text="somewhere on the page\nthere's a mood that fits.", bg="#F1D7E3", fg=INK_SOFT, font=BODY, justify="left").pack(anchor="w", pady=(18,0))

# Choice pieces use the same existing options/functionality, but are visually different.
choices = tk.Frame(vibe_stage, bg=CREAM)
choices.grid(row=0, column=1, sticky="nsew")
vibe_buttons_state = []

# ============================================================
# CAMERA / DEEPFACE STATE
# ============================================================
camera = None
camera_running = False
analyzing = False


def show_vibe_options(emotion):
    global last_emotion
    last_emotion = emotion
    emotion_label.config(text=f"YOUR MOOD IS... {emotion.upper()}")
    emotion_big.config(text=emotion.upper())
    message_label.config(text={
        "sad": "rough one? okay. let's find something that knows how to sit beside it.",
        "angry": "yeah. the soundtrack needs to understand the assignment.",
        "happy": "wait, keep this one. i don't want this mood leaving yet.",
        "neutral": "hmm. mysterious. i like it. let's see what happens.",
        "fear": "gentle tonight. no need to make the room louder than it already is.",
        "surprise": "you clearly have a story. we'll let the music catch up.",
        "disgust": "nope. we're throwing that energy out and choosing again.",
    }.get(emotion, "interesting. your face is keeping secrets today."))
    vibe_gossip_label.config(text=rotate_emotion_gossip(emotion))

    for b in vibe_buttons_state:
        try:
            b.destroy()
        except tk.TclError:
            pass
    vibe_buttons_state.clear()

    options = {
        "sad": ["make me feel better", "romanticise the situation", "stare out the window", "leave me alone, but with music", "surprise me"],
        "angry": ["match my energy", "calm me down", "main character mode", "let me scream musically", "surprise me"],
        "happy": ["keep this going", "make me dance", "main character mode", "throwbacks", "surprise me"],
        "neutral": ["wake me up", "cozy mode", "make me dance", "late-night brain", "surprise me"],
        "fear": ["calm me down", "something soft", "comfort zone", "distract me", "surprise me"],
        "surprise": ["give me chaos", "make me dance", "hype me up", "something unexpected", "surprise me"],
        "disgust": ["cleanse my ears", "something comforting", "give me energy", "change the mood", "surprise me"],
    }.get(emotion, ["surprise me"])

    colours = ["#F7C8E0", "#AEE8E8", "#FFD98E", "#C9A7FF", "#B8E986", "#FF8F8F", "#91B8E8"]
    scribbles = ["keep", "hmm", "maybe", "this one", "obviously", "for tonight", "circle this"]
    positions = [
        (0.03, 0.03, 0.43, 0.28),
        (0.52, 0.02, 0.43, 0.27),
        (0.08, 0.35, 0.39, 0.28),
        (0.53, 0.38, 0.40, 0.29),
        (0.28, 0.70, 0.45, 0.24),
    ]

    for index, option in enumerate(options):
        relx, rely, relw, relh = positions[index % len(positions)]
        holder = tk.Frame(choices, bg="#342037", padx=2, pady=2)
        holder.place(relx=relx, rely=rely, relwidth=relw, relheight=relh)
        card_bg = colours[index % len(colours)]
        card = tk.Frame(holder, bg=card_bg, highlightthickness=1, highlightbackground="#8A5870")
        card.pack(fill="both", expand=True)
        tk.Label(card, text=random.choice(scribbles), bg=card_bg, fg=INK_SOFT, font=HAND).pack(anchor="w", padx=9, pady=(5, 0))
        button = tk.Button(card, text=option, command=lambda value=option: choose_vibe(value), bg=card_bg, fg=INK, activebackground=WHITE, activeforeground=INK, font=(TITLE_FACE, 11, "bold"), relief="flat", bd=0, cursor="hand2", wraplength=190, justify="left", anchor="w", padx=13, pady=6)
        button.pack(fill="both", expand=True)
        button.bind("<Enter>", lambda e, b=button, c=card_bg: (b.configure(relief="raised", bd=1), b.master.configure(bg=WHITE)))
        button.bind("<Leave>", lambda e, b=button, c=card_bg: (b.configure(relief="flat", bd=0), b.master.configure(bg=c)))
        holder.button = button
        vibe_buttons_state.append(holder)

    window.after(80, lambda: show_screen(vibe_frame))


# ============================================================
# CAMERA FUNCTIONS
# ============================================================
def open_camera():
    global camera, camera_running
    show_screen(camera_frame)
    camera_gossip_label.config(text=rotate_text("gossip"))
    camera_fact_label.config(text=rotate_text("facts"))
    try:
        if camera is not None:
            camera.release()
        camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    except Exception:
        camera = None

    if camera is None or not camera.isOpened():
        camera_hint = "camera couldn't open — check permissions"
        popup("camera issue", camera_hint)
        return

    camera_running = True
    window.focus_force()
    update_camera()


def update_camera():
    global camera_running
    if not camera_running or camera is None:
        return
    success, frame = camera.read()
    if success:
        display = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        # Dreamy preview only; DeepFace still receives the original frame.
        pil = ImageEnhance.Color(pil).enhance(0.78)
        pil = ImageEnhance.Contrast(pil).enhance(0.93)
        pil = ImageEnhance.Brightness(pil).enhance(1.03)
        pil = pil.filter(ImageFilter.GaussianBlur(0.18))
        pil.thumbnail((760, 560), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(pil)
        camera_label.configure(image=photo)
        camera_label.image = photo
    window.after(30, update_camera)


def capture_photo():
    global camera, camera_running
    if not camera_running or camera is None:
        return
    success, frame = camera.read()
    if not success:
        popup("camera issue", "the camera gave us a blank frame. try once more ♡")
        return
    cv2.imwrite(str(Path("captured_face.jpg").resolve()), frame)
    camera_running = False
    camera.release()
    camera = None
    camera_label.configure(image="")
    # Keep the known-working direct DeepFace path.
    window.after(120, analyze_emotion)


def cancel_camera():
    global camera, camera_running
    camera_running = False
    if camera is not None:
        camera.release()
        camera = None
    camera_label.configure(image="")
    show_screen(home_frame)


def analyze_emotion():
    global last_emotion, analyzing
    if analyzing:
        return
    analyzing = True
    try:
        result = DeepFace.analyze(img_path=str(Path("captured_face.jpg").resolve()), actions=["emotion"])
        emotion = result[0]["dominant_emotion"]
        last_emotion = emotion
        analyzing = False
        show_vibe_options(emotion)
    except Exception as exc:
        analyzing = False
        print("DeepFace error:", repr(exc))
        popup("mood check", "DeepFace couldn't read that frame.\n\nTry the photo once more — your camera can stay open.")
        show_screen(camera_frame)


# ============================================================
# ============================================================
# RESULTS / COVER LOADING — safe queue, local cache, small shelf
# ============================================================
cover_executor = ThreadPoolExecutor(max_workers=32)
cover_queue = queue.Queue()
cover_cache_dir = Path(".cover_cache_bratz")
cover_cache_dir.mkdir(exist_ok=True)
cover_photo_refs = []
cover_generation = 0
current_songs = []
current_vibe = ""


def cover_cache_path(url):
    digest = hashlib.md5(url.encode("utf-8")).hexdigest()
    return cover_cache_dir / f"{digest}.jpg"


def fetch_cover_job(generation, index, url, title):
    """Background network work only. Never touches Tkinter."""
    if not url:
        cover_queue.put((generation, index, None, "missing"))
        return

    path = cover_cache_path(url)
    try:
        if path.exists() and path.stat().st_size > 1000:
            cover_queue.put((generation, index, str(path), None))
            return

        response = requests.get(
            url,
            timeout=(2.0, 4.0),
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response.raise_for_status()
        image = Image.open(BytesIO(response.content)).convert("RGB")
        image.thumbnail((220, 220), Image.Resampling.LANCZOS)
        image.save(path, "JPEG", quality=88, optimize=True)
        cover_queue.put((generation, index, str(path), None))
    except Exception as exc:
        cover_queue.put((generation, index, None, str(exc)))


def build_result_card(parent, song, index, generation):
    card_colors = ["#FFF8FB", "#F3ECFF", "#EAF9F9", "#FFF6D8", "#F6F0FF", "#FDE8EF"]
    accents = ["#F178AE", "#8E6BCE", "#63BFC2", "#E8B949", "#A98AE5", "#D84C79"]
    card_bg = card_colors[index % len(card_colors)]
    accent = accents[index % len(accents)]

    # Looks like a collected sleeve/page, not a SaaS result tile.
    card = tk.Frame(parent, bg="#3A2334", width=248, height=338)
    card.grid_propagate(False)
    page = tk.Frame(card, bg=card_bg, highlightthickness=2, highlightbackground=accent, padx=10, pady=8)
    page.pack(fill="both", expand=True)

    top = tk.Frame(page, bg=card_bg)
    top.pack(fill="x")
    label_text = ["found this", "keep this", "little find", "file this", "maybe yours", "don't skip"][index % 6]
    tk.Label(top, text=label_text, bg=accent, fg=INK, font=HAND, padx=6, pady=1).pack(side="left")
    tk.Label(top, text=f"#{index+1:02d}", bg=card_bg, fg=INK_SOFT, font=SMALL).pack(side="right")

    # Cover holder remains the exact attribute used by the existing safe queue.
    holder = tk.Frame(page, bg="#25202D", highlightthickness=3, highlightbackground=accent, width=208, height=208)
    holder.pack(pady=(8, 8))
    holder.pack_propagate(False)
    label = tk.Label(holder, text="developing...", bg="#332C3B", fg="#F7EFF8", font=HAND, cursor="hand2", justify="center")
    label.place(x=6, y=6, width=196, height=196)
    label.bind("<Button-1>", lambda e, u=song.get("spotify_url"): open_spotify(u))

    tk.Label(page, text=song.get("title", "Untitled"), bg=card_bg, fg=INK, font=BODY_BOLD, wraplength=214, justify="left", anchor="w").pack(fill="x", padx=3)
    tk.Label(page, text=song.get("artist", "Unknown artist"), bg=card_bg, fg=INK_SOFT, font=SMALL, wraplength=214, justify="left", anchor="w").pack(fill="x", padx=3, pady=(2, 0))
    tk.Label(page, text="tap the picture → Spotify", bg=card_bg, fg=accent, font=HAND).pack(anchor="w", padx=3, pady=(5,0))

    card.cover_label = label
    card.cover_url = song.get("cover_url")
    card.song_index = index
    card.cover_generation = generation
    return card

def build_results_grid(songs):
    global cover_generation
    cover_generation += 1
    generation = cover_generation

    cover_photo_refs.clear()
    try:
        while True:
            cover_queue.get_nowait()
    except queue.Empty:
        pass

    for widget in results_grid.winfo_children():
        widget.destroy()

    # Keep every song returned for this vibe. Nothing is hidden behind a
    # six-song demo limit; the results panel is scrollable.
    display_songs = list(songs)

    for col in range(3):
        results_grid.grid_columnconfigure(col, weight=1, uniform="records")

    for index, song in enumerate(display_songs):
        card = build_result_card(results_grid, song, index, generation)
        card.grid(row=index // 3, column=index % 3, padx=9, pady=9, sticky="n")
        if card.cover_url:
            cover_executor.submit(fetch_cover_job, generation, index, card.cover_url, song.get("title", "song"))

    results_grid.update_idletasks()
    results_canvas.configure(scrollregion=results_canvas.bbox("all"))


def pump_cover_queue():
    try:
        while True:
            generation, index, path, error = cover_queue.get_nowait()
            if generation != cover_generation:
                continue

            card = next((w for w in results_grid.winfo_children()
                         if getattr(w, "song_index", None) == index
                         and getattr(w, "cover_generation", None) == generation), None)
            if card is None or not card.winfo_exists():
                continue

            if path:
                try:
                    with Image.open(path) as source:
                        image = source.convert("RGB").copy()
                    photo = ImageTk.PhotoImage(image)
                    cover_photo_refs.append(photo)
                    card.cover_label.configure(image=photo, text="")
                    card.cover_label.image = photo
                except Exception as exc:
                    print("Cover display error:", repr(exc))
                    card.cover_label.configure(text="♡ cover shy today")
            elif error == "missing":
                card.cover_label.configure(text="♡ no cover yet")
            else:
                card.cover_label.configure(text="♡ cover shy today")
    except queue.Empty:
        pass

    if window.winfo_exists():
        window.after(60, pump_cover_queue)


def show_results(songs, vibe):
    global current_songs, current_vibe
    current_songs = list(songs)
    current_vibe = vibe
    results_title.config(text="your soundtrack ♡")
    results_subtitle.config(text=f"{vibe.lower()}  ·  {len(current_songs)} little picks")
    results_gossip.config(text=rotate_emotion_gossip(last_emotion))
    build_results_grid(current_songs)
    show_screen(results_frame)


def surprise_song():
    if current_songs:
        open_spotify(random.choice(current_songs).get("spotify_url"))


# -----------------------------
# RESULTS SCREEN — opening a drawer full of found songs
results_top = tk.Frame(results_frame, bg=CREAM, height=43)
results_top.pack(fill="x")
results_top.pack_propagate(False)
results_title = tk.Label(results_top, text="WAIT. I THINK I FOUND SOMETHING.", bg=CREAM, fg=HOT_PINK, font=HEAD)
results_title.pack(side="left")
results_subtitle = tk.Label(results_top, text="", bg=CREAM, fg=INK_SOFT, font=HAND)
results_subtitle.pack(side="left", padx=10)
results_gossip = tk.Label(results_top, text="", bg=CREAM, fg=INK_SOFT, font=HAND, wraplength=390, justify="left")
results_gossip.pack(side="right", padx=9)

results_paper = tk.Frame(results_frame, bg="#24182E", highlightthickness=2, highlightbackground="#6B3552", padx=8, pady=8)
results_paper.pack(fill="both", expand=True)
archive_note = tk.Frame(results_paper, bg="#F7C8E0", highlightthickness=1, highlightbackground="#B74F7B", padx=12, pady=8)
archive_note.pack(fill="x", padx=4, pady=(0, 7))
tk.Label(archive_note, text="THE MUSIC DRAWER / pull something out", bg="#F7C8E0", fg="#7A274E", font=BODY_BOLD).pack(anchor="w")
tk.Label(archive_note, text="there's no 'top 5'. take your time. the whole shelf is here.", bg="#F7C8E0", fg=INK, font=HAND).pack(anchor="w", pady=(2,0))

results_canvas = tk.Canvas(results_paper, bg="#24182E", highlightthickness=0, bd=0)
results_scroll = tk.Scrollbar(results_paper, orient="vertical", command=results_canvas.yview)
results_scroll.pack(side="right", fill="y")
results_canvas.pack(side="left", fill="both", expand=True)
results_canvas.configure(yscrollcommand=results_scroll.set)
results_grid = tk.Frame(results_canvas, bg="#24182E")
results_window_id = results_canvas.create_window((0, 0), window=results_grid, anchor="nw")

def resize_results(event):
    results_canvas.itemconfigure(results_window_id, width=event.width)
    results_canvas.configure(scrollregion=results_canvas.bbox("all"))

def update_results_region(event=None):
    results_canvas.configure(scrollregion=results_canvas.bbox("all"))

results_canvas.bind("<Configure>", resize_results)
results_grid.bind("<Configure>", update_results_region)
results_canvas.bind("<MouseWheel>", lambda e: results_canvas.yview_scroll(-int(e.delta / 120), "units"))
results_bottom = tk.Frame(results_frame, bg=CREAM, height=40)
results_bottom.pack(fill="x", pady=(6,0))
results_bottom.pack_propagate(False)
world_object(results_bottom, "← another feeling", "#F7C8E0", command=lambda: show_vibe_options(last_emotion), font=HAND, padx=10, pady=5).pack(side="left", padx=2)
world_object(results_bottom, "✦ surprise me", "#C9A7FF", command=surprise_song, font=HAND, padx=10, pady=5).pack(side="left", padx=2)
world_object(results_bottom, "open the gossip", "#FFD98E", command=show_gossip_popup, font=HAND, padx=10, pady=5).pack(side="left", padx=2)
tk.Button(results_bottom, text="⌂ my little page", command=lambda: show_screen(home_frame), bg="#AEE8E8", fg=INK, relief="raised", bd=1, font=BODY_BOLD, cursor="hand2", padx=12, pady=5).pack(side="right")

# VIBE LOADING — only the choices area changes
# ============================================================
vibe_busy_overlay = tk.Frame(vibe_frame, bg=PAPER, highlightthickness=1, highlightbackground=BORDER, padx=28, pady=22)
vibe_busy_label = tk.Label(vibe_busy_overlay, text="", bg=PAPER, fg=INK, font=HEAD, justify="center")
vibe_busy_label.pack()
vibe_busy_sub = tk.Label(vibe_busy_overlay, text="", bg=PAPER, fg=INK_SOFT, font=HAND, justify="center")
vibe_busy_sub.pack(pady=(5, 0))

music_executor = ThreadPoolExecutor(max_workers=1)
ui_queue = queue.Queue()
request_token = 0


def set_vibe_buttons_enabled(enabled):
    state = "normal" if enabled else "disabled"
    for holder in vibe_buttons_state:
        try:
            holder.button.configure(state=state)
        except Exception:
            pass


def choose_vibe(vibe):
    global request_token
    request_token += 1
    token = request_token

    database_vibe = {
        "make me feel better": "comfort",
        "romanticise the situation": "romantic",
        "stare out the window": "calm",
        "leave me alone, but with music": "calm",
        "match my energy": "angry_energy",
        "calm me down": "calm",
        "main character mode": "main_character",
        "let me scream musically": "angry_energy",
        "keep this going": "happy",
        "make me dance": "dance",
        "throwbacks": "throwback",
        "wake me up": "energy",
        "cozy mode": "cozy",
        "late-night brain": "late_night",
        "something soft": "soft",
        "comfort zone": "comfort",
        "distract me": "distraction",
        "give me chaos": "chaos",
        "hype me up": "hype",
        "something unexpected": "surprise",
        "cleanse my ears": "fresh",
        "something comforting": "comfort",
        "give me energy": "energy",
        "change the mood": "mood_change",
        "surprise me": "surprise",
    }.get(vibe, vibe.lower())

    set_vibe_buttons_enabled(False)
    vibe_busy_label.config(text=random.choice([
        "♡ opening the music box...",
        "✦ finding your little soundtrack...",
        "flipping through the mixtape...",
        "finding your 1 a.m. song...",
    ]))
    vibe_busy_sub.config(text=rotate_text("vibe"))
    vibe_busy_overlay.place(relx=0.60, rely=0.53, anchor="center")

    def worker():
        try:
            songs = get_songs_by_vibe(database_vibe, limit=1000)
            error = None
        except Exception as exc:
            songs = []
            error = exc
        ui_queue.put(("songs", token, vibe, songs, error))

    # One request at a time. Clicking while loading is disabled.
    music_executor.submit(worker)

def pump_ui_queue():
    try:
        while True:
            kind, token, vibe, songs, error = ui_queue.get_nowait()
            if kind != "songs" or token != request_token:
                continue

            vibe_busy_overlay.place_forget()
            set_vibe_buttons_enabled(True)

            if error is not None:
                popup("music shelf", "the shelf took a tiny nap.\ntry that mood once more ♡")
                continue
            if not songs:
                popup("music shelf", "nothing on that shelf yet ♡\ntry another mood.")
                continue

            show_results(songs, vibe)
    except queue.Empty:
        pass

    if window.winfo_exists():
        window.after(50, pump_ui_queue)


# ============================================================
# NAV — like coloured tabs in a magazine, not a SaaS header
# ============================================================
nav_items = [
    ("my page", lambda: show_screen(home_frame), "#F7C8E0"),
    ("photo booth", lambda: open_camera(), "#AEE8E8"),
    ("mood page", show_mood_note, "#B8E986"),
    ("music drawer", show_current_music, "#C9A7FF"),
    ("gossip", show_gossip_popup, "#FFD98E"),
]
for label, command, color in nav_items:
    b = tk.Label(nav, text=label, bg=color, fg=INK, font=BODY_BOLD, cursor="hand2", padx=11, pady=4)
    b.pack(side="left", padx=3, pady=3)
    b.bind("<Button-1>", lambda e, c=command: c())
    b.bind("<Enter>", lambda e, w=b: w.config(bg=WHITE))
    b.bind("<Leave>", lambda e, w=b, c=color: w.config(bg=c))
tk.Label(nav, text="♡ still awake?", bg="#24182E", fg="#F7C8E0", font=HAND).pack(side="right", padx=11)

# ============================================================
# CAMERA KEYBOARD
# ============================================================
def keyboard_capture(event):
    if not camera_running:
        return
    if event.keysym == "space":
        capture_photo()
    elif event.keysym.lower() == "q":
        cancel_camera()

window.bind("<Key>", keyboard_capture)


def close_app():
    global camera, camera_running
    camera_running = False
    if camera is not None:
        camera.release()
        camera = None
    for executor in (cover_executor, music_executor):
        try:
            executor.shutdown(wait=False, cancel_futures=True)
        except Exception:
            pass
    window.destroy()

window.protocol("WM_DELETE_WINDOW", close_app)

# Start background pumps.
window.after(60, pump_ui_queue)
window.after(60, pump_cover_queue)
show_screen(home_frame)
window.mainloop()