import tkinter as tk
import random
import cv2
import os
import webbrowser
import requests

from io import BytesIO
from PIL import Image, ImageTk
from deepface import DeepFace
from dotenv import load_dotenv
from supabase import create_client


# ============================================================
# NIGHT FURRY
# ============================================================

BG = "#070817"
SURFACE = "#101329"
SURFACE_2 = "#171A38"

WHITE = "#F8F7FF"
MUTED = "#A8AAC8"

PURPLE = "#8B5CF6"
PURPLE_LIGHT = "#A78BFA"
PINK = "#FF4FA3"
CYAN = "#35D6FF"
ORANGE = "#FFB84D"
MINT = "#55E6B5"


# Fonts are chosen from common Windows fonts.
AVAILABLE_FONTS = set()

try:
    import tkinter.font as tkfont
    AVAILABLE_FONTS = set(tkfont.families())
except Exception:
    pass


def pick_font(options):
    for font_name in options:
        if not AVAILABLE_FONTS or font_name in AVAILABLE_FONTS:
            return font_name
    return options[-1]


TITLE_FACE = pick_font([
    "Century Gothic",
    "Gill Sans MT",
    "Segoe UI",
    "Trebuchet MS"
])

BODY_FACE = pick_font([
    "Segoe UI",
    "Trebuchet MS",
    "Arial"
])

ACCENT_FACE = pick_font([
    "Segoe Print",
    "Comic Sans MS",
    "Segoe UI"
])


TITLE_FONT = (TITLE_FACE, 58, "bold")
HEADING_FONT = (TITLE_FACE, 34, "bold")
BODY_FONT = (BODY_FACE, 15)
BUTTON_FONT = (BODY_FACE, 13, "bold")
SMALL_FONT = (BODY_FACE, 10)
ACCENT_FONT = (ACCENT_FACE, 11)


# ============================================================
# SUPABASE
# ============================================================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


def get_songs_by_vibe(vibe):
    response = (
        supabase
        .table("songs")
        .select("*")
        .eq("vibe", vibe.lower())
        .execute()
    )

    return response.data


def open_spotify(url):
    if url:
        webbrowser.open(url)


# ============================================================
# CAMERA STATE
# ============================================================

camera = None
camera_running = False

# Keeps album cover images alive inside Tkinter
cover_photo_refs = []


# ============================================================
# MAIN WINDOW
# ============================================================

window = tk.Tk()
window.title("night furry")
window.configure(bg=BG)

try:
    window.state("zoomed")
except tk.TclError:
    window.geometry("1280x800")

window.minsize(950, 650)


# ============================================================
# BACKGROUND CANVAS
# ============================================================

canvas = tk.Canvas(
    window,
    bg=BG,
    highlightthickness=0
)

canvas.pack(fill="both", expand=True)


# ============================================================
# BACKGROUND DECOR
# ============================================================

canvas.create_oval(
    -180, -220, 250, 180,
    fill="#17133A",
    outline=""
)

canvas.create_oval(
    1050, -180, 1450, 210,
    fill="#21143E",
    outline=""
)

canvas.create_oval(
    -140, 650, 250, 1050,
    fill="#101F3D",
    outline=""
)

canvas.create_oval(
    1120, 650, 1530, 1050,
    fill="#281536",
    outline=""
)


# ============================================================
# FLOATING PARTICLES
# ============================================================

particles = []

particle_colours = [
    "#FFFFFF",
    "#BCA7FF",
    "#FF75B9",
    "#44D9FF",
    "#FFC857",
    "#63E6BE"
]

for _ in range(120):

    x = random.randint(0, 1700)
    y = random.randint(0, 1000)

    size = random.choice([
        1, 1, 1,
        2, 2,
        3
    ])

    particle = canvas.create_oval(
        x,
        y,
        x + size,
        y + size,
        fill=random.choice(particle_colours),
        outline=""
    )

    particles.append({
        "id": particle,
        "x": x,
        "y": y,
        "speed": random.uniform(0.08, 0.35),
        "size": size,
        "twinkle": random.random()
    })


def animate_background():

    width = max(
        window.winfo_width(),
        1000
    )

    height = max(
        window.winfo_height(),
        700
    )

    for p in particles:

        p["y"] += p["speed"]

        if p["y"] > height + 10:

            p["y"] = -10
            p["x"] = random.randint(
                0,
                width
            )

        p["twinkle"] += 0.035

        canvas.coords(
            p["id"],
            p["x"],
            p["y"],
            p["x"] + p["size"],
            p["y"] + p["size"]
        )

    window.after(
        45,
        animate_background
    )


animate_background()


# ============================================================
# MAIN CONTENT
# ============================================================

main_frame = tk.Frame(
    canvas,
    bg=BG
)

main_window = canvas.create_window(
    0,
    0,
    window=main_frame,
    anchor="center"
)


def center_content(event=None):

    canvas.coords(
        main_window,
        window.winfo_width() // 2,
        window.winfo_height() // 2
    )


window.bind(
    "<Configure>",
    center_content
)


# ============================================================
# SCREEN SWITCHING
# ============================================================

home_frame = tk.Frame(
    main_frame,
    bg=BG
)

camera_frame = tk.Frame(
    main_frame,
    bg=BG
)

vibe_frame = tk.Frame(
    main_frame,
    bg=BG
)


def show_only(frame):

    for f in [
        home_frame,
        camera_frame,
        vibe_frame
    ]:
        f.pack_forget()

    frame.pack()


# ============================================================
# SMALL TOP BRAND
# ============================================================

def make_brand(parent):

    brand = tk.Label(
        parent,
        text="night furry",
        bg=BG,
        fg=PINK,
        font=(TITLE_FACE, 25, "bold")
    )

    brand.pack(
        pady=(0, 18)
    )

    return brand


# ============================================================
# HOME SCREEN
# ============================================================

make_brand(home_frame)

home_kicker = tk.Label(
    home_frame,
    text="your playlist called. it wants better material.",
    bg=BG,
    fg=CYAN,
    font=(BODY_FACE, 11, "bold")
)

home_kicker.pack(
    pady=(0, 14)
)


home_title = tk.Label(
    home_frame,
    text="what's the soundtrack\nin your head?",
    bg=BG,
    fg=WHITE,
    font=TITLE_FONT,
    justify="center"
)

home_title.pack()


home_subtitle = tk.Label(
    home_frame,
    text=(
        "let the camera make one questionable assumption about your face.\n"
        "then you decide what happens next."
    ),
    bg=BG,
    fg=MUTED,
    font=BODY_FONT,
    justify="center"
)

home_subtitle.pack(
    pady=(14, 25)
)


# ============================================================
# HOME STATUS CARD
# ============================================================

status_card = tk.Frame(
    home_frame,
    bg=SURFACE,
    padx=28,
    pady=15
)

status_card.pack(
    pady=(0, 22)
)


status_dot = tk.Label(
    status_card,
    text="●",
    bg=SURFACE,
    fg=MINT,
    font=(BODY_FACE, 10)
)

status_dot.pack(
    side="left",
    padx=(0, 8)
)


status_label = tk.Label(
    status_card,
    text="currently pretending this counts as self-care",
    bg=SURFACE,
    fg=WHITE,
    font=BODY_FONT
)

status_label.pack(
    side="left"
)


home_messages = [
    "currently pretending this counts as self-care",
    "your screen time report remains confidential",
    "one song. then bed. obviously.",
    "you opened this instead of sleeping. fair.",
    "the algorithm cannot judge you. probably.",
    "we're just here for the soundtrack.",
    "no thoughts. just extremely specific music.",
    "your headphones have seen things.",
    "this is significantly more productive than doomscrolling. technically."
]


def rotate_home_message():

    status_label.config(
        text=random.choice(home_messages)
    )

    window.after(
        3000,
        rotate_home_message
    )


rotate_home_message()


# ============================================================
# PRIMARY BUTTON
# ============================================================

def button_enter(event):

    event.widget.configure(
        bg=PURPLE_LIGHT,
        fg=BG
    )


def button_leave(event):

    event.widget.configure(
        bg=PURPLE,
        fg=WHITE
    )


def primary_button(parent, text, command):

    button = tk.Button(
        parent,
        text=text,
        command=command,
        bg=PURPLE,
        fg=WHITE,
        activebackground=PURPLE_LIGHT,
        activeforeground=BG,
        font=(BODY_FACE, 14, "bold"),
        relief="flat",
        bd=0,
        cursor="hand2",
        padx=45,
        pady=16
    )

    button.bind(
        "<Enter>",
        button_enter
    )

    button.bind(
        "<Leave>",
        button_leave
    )

    return button


# ============================================================
# OPEN CAMERA
# ============================================================

def open_camera():

    global camera
    global camera_running

    show_only(camera_frame)

    camera_title.config(
        text="give me your best\n'yeah i'm fine' face."
    )

    camera_hint.config(
        text="SPACE to capture   •   Q to go back"
    )

    camera = cv2.VideoCapture(
        0,
        cv2.CAP_DSHOW
    )

    if not camera.isOpened():

        camera_title.config(
            text="the camera said no."
        )

        camera_hint.config(
            text="check camera permissions and try again."
        )

        return

    camera_running = True

    window.focus_force()

    update_camera()


# ============================================================
# CAMERA SCREEN
# ============================================================

make_brand(camera_frame)

camera_kicker = tk.Label(
    camera_frame,
    text="okay. camera time.",
    bg=BG,
    fg=CYAN,
    font=(BODY_FACE, 11, "bold")
)

camera_kicker.pack(
    pady=(0, 10)
)


camera_title = tk.Label(
    camera_frame,
    text="give me your best\n'yeah i'm fine' face.",
    bg=BG,
    fg=WHITE,
    font=HEADING_FONT,
    justify="center"
)

camera_title.pack()


camera_hint = tk.Label(
    camera_frame,
    text="SPACE to capture   •   Q to go back",
    bg=BG,
    fg=MUTED,
    font=SMALL_FONT
)

camera_hint.pack(
    pady=(8, 16)
)


camera_card = tk.Frame(
    camera_frame,
    bg=SURFACE_2,
    padx=12,
    pady=12
)

camera_card.pack()


camera_label = tk.Label(
    camera_card,
    bg=SURFACE_2
)

camera_label.pack()


camera_tip = tk.Label(
    camera_frame,
    text="the algorithm is about to make one tiny assumption.",
    bg=BG,
    fg=MUTED,
    font=SMALL_FONT
)

camera_tip.pack(
    pady=14
)


# ============================================================
# LIVE CAMERA
# ============================================================

def update_camera():

    global camera_running

    if not camera_running:
        return

    success, frame = camera.read()

    if success:

        display_frame = cv2.flip(
            frame,
            1
        )

        display_frame = cv2.cvtColor(
            display_frame,
            cv2.COLOR_BGR2RGB
        )

        display_frame = Image.fromarray(
            display_frame
        )

        display_frame = display_frame.resize(
            (620, 465)
        )

        photo = ImageTk.PhotoImage(
            display_frame
        )

        camera_label.config(
            image=photo
        )

        camera_label.image = photo

    window.after(
        10,
        update_camera
    )


# ============================================================
# CAPTURE
# ============================================================

def capture_photo():

    global camera
    global camera_running

    if not camera_running:
        return

    success, frame = camera.read()

    if success:

        cv2.imwrite(
            "captured_face.jpg",
            frame
        )

    camera_running = False

    if camera is not None:

        camera.release()
        camera = None

    camera_label.config(
        image=""
    )

    camera_title.config(
        text="okay.\nprocessing the evidence..."
    )

    camera_hint.config(
        text="please remain emotionally available."
    )

    window.after(
        700,
        analyze_emotion
    )


# ============================================================
# CANCEL CAMERA
# ============================================================

def cancel_camera():

    global camera
    global camera_running

    camera_running = False

    if camera is not None:

        camera.release()
        camera = None

    camera_label.config(
        image=""
    )

    show_only(home_frame)


# ============================================================
# CAMERA START BUTTON
# ============================================================

start_button = primary_button(
    home_frame,
    "read my face  →",
    lambda: open_camera()
)

start_button.pack()


home_note = tk.Label(
    home_frame,
    text="no questionnaire. no personality test. just music.",
    bg=BG,
    fg=MUTED,
    font=SMALL_FONT
)

home_note.pack(
    pady=(16, 0)
)


# ============================================================
# VIBE SCREEN
# ============================================================

make_brand(vibe_frame)

emotion_kicker = tk.Label(
    vibe_frame,
    text="apparently, your face has lore.",
    bg=BG,
    fg=PINK,
    font=(BODY_FACE, 11, "bold")
)

emotion_kicker.pack(
    pady=(0, 10)
)


emotion_label = tk.Label(
    vibe_frame,
    text="",
    bg=BG,
    fg=WHITE,
    font=(TITLE_FACE, 48, "bold")
)

emotion_label.pack()


message_label = tk.Label(
    vibe_frame,
    text="",
    bg=BG,
    fg=MUTED,
    font=BODY_FONT,
    wraplength=700,
    justify="center"
)

message_label.pack(
    pady=(12, 25)
)


question_label = tk.Label(
    vibe_frame,
    text="so... what are we doing about it?",
    bg=BG,
    fg=WHITE,
    font=(BODY_FACE, 15, "bold")
)

question_label.pack(
    pady=(0, 18)
)


buttons_container = tk.Frame(
    vibe_frame,
    bg=BG
)

buttons_container.pack(
    fill="both",
    expand=True
)


vibe_footer = tk.Label(
    vibe_frame,
    text="pick one. there are no wrong answers, only questionable playlists.",
    bg=BG,
    fg=MUTED,
    font=SMALL_FONT
)

vibe_footer.pack(
    pady=(12, 0)
)


# ============================================================
# EMOTION MESSAGES
# ============================================================

messages = {

    "sad":
        "rough one?\n"
        "we're not fixing your life. we're finding something to play while you exist.",

    "angry":
        "yeah. we got the memo.\n"
        "let's put that energy somewhere productive-ish.",

    "happy":
        "oh, you're actually having a good day.\n"
        "rare footage. let's use it.",

    "neutral":
        "your face has chosen diplomacy.\n"
        "interesting. let's give it a soundtrack.",

    "fear":
        "okay. breathe.\n"
        "we're going somewhere a little softer.",

    "surprise":
        "something clearly happened.\n"
        "we have absolutely no context.",

    "disgust":
        "yeah... whatever that was,\n"
        "it does not deserve a boring soundtrack."
}


# ============================================================
# VIBE OPTIONS
# ============================================================

vibe_options = {

    "sad": [
        "make me feel better",
        "romanticise the situation",
        "stare out the window",
        "leave me alone, but with music",
        "surprise me"
    ],

    "angry": [
        "match my energy",
        "calm me down",
        "main character mode",
        "let me scream musically",
        "surprise me"
    ],

    "happy": [
        "keep this going",
        "make me dance",
        "main character mode",
        "throwbacks",
        "surprise me"
    ],

    "neutral": [
        "wake me up",
        "cozy mode",
        "make me dance",
        "late-night brain",
        "surprise me"
    ],

    "fear": [
        "calm me down",
        "something soft",
        "comfort zone",
        "distract me",
        "surprise me"
    ],

    "surprise": [
        "give me chaos",
        "make me dance",
        "hype me up",
        "something unexpected",
        "surprise me"
    ],

    "disgust": [
        "cleanse my ears",
        "something comforting",
        "give me energy",
        "change the mood",
        "surprise me"
    ]
}


# ============================================================
# VIBE MAP
# ============================================================

VIBE_MAP = {

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

    "surprise me": "surprise"
}


# ============================================================
# VIBE BUTTON
# ============================================================

button_colours = [
    PURPLE,
    "#272B52",
    "#272B52",
    "#272B52",
    "#272B52"
]


def choose_vibe_button(parent, text, index):

    normal_colour = button_colours[
        min(
            index,
            len(button_colours) - 1
        )
    ]

    button = tk.Button(
        parent,
        text=text,
        font=BUTTON_FONT,
        bg=normal_colour,
        fg=WHITE,
        activebackground=PURPLE_LIGHT,
        activeforeground=BG,
        relief="flat",
        bd=0,
        cursor="hand2",
        padx=22,
        pady=12,
        command=lambda: choose_vibe(text)
    )

    def enter(event):

        event.widget.configure(
            bg=PURPLE,
            fg=WHITE
        )

    def leave(event):

        event.widget.configure(
            bg=normal_colour,
            fg=WHITE
        )

    button.bind(
        "<Enter>",
        enter
    )

    button.bind(
        "<Leave>",
        leave
    )

    return button


# ============================================================
# SHOW VIBES
# ============================================================

def show_vibe_options(emotion):

    show_only(vibe_frame)

    emotion_label.config(
        text=emotion.upper()
    )

    message_label.config(
        text=messages.get(
            emotion,
            "interesting. your face has entered mysterious territory."
        )
    )

    question_label.config(
        text="so... what are we doing about it?"
    )

    for widget in buttons_container.winfo_children():
        widget.destroy()

    options = vibe_options.get(
        emotion,
        ["surprise me"]
    )

    # Two-column layout
    for index, vibe in enumerate(options):

        row = index // 2
        column = index % 2

        button = choose_vibe_button(
            buttons_container,
            vibe,
            index
        )

        button.grid(
            row=row,
            column=column,
            padx=6,
            pady=6,
            ipadx=16
        )


# ============================================================
# CHOOSE VIBE
# ============================================================

def choose_vibe(vibe):

    global cover_photo_refs

    emotion_label.config(
        text="LOCKED IN."
    )

    message_label.config(
        text=(
            f'"{vibe}"\n\n'
            "okay. finding something for the headphones..."
        )
    )

    question_label.config(
        text="your soundtrack is loading."
    )

    for widget in buttons_container.winfo_children():
        widget.destroy()

    cover_photo_refs.clear()

    database_vibe = VIBE_MAP.get(
        vibe,
        vibe.lower()
    )

    try:

        songs = get_songs_by_vibe(
            database_vibe
        )

    except Exception as error:

        print(
            "Supabase error:",
            error
        )

        error_label = tk.Label(
            buttons_container,
            text="couldn't reach the music library.",
            bg=BG,
            fg=MUTED,
            font=BODY_FONT
        )

        error_label.pack(
            pady=20
        )

        return

    if not songs:

        no_song_label = tk.Label(
            buttons_container,
            text=f'No songs found for "{vibe}" yet.',
            bg=BG,
            fg=MUTED,
            font=BODY_FONT
        )

        no_song_label.pack(
            pady=20
        )

        return

    # ========================================================
    # SCROLLABLE SONG AREA
    # ========================================================

    scroll_area = tk.Frame(
        buttons_container,
        bg=BG
    )

    scroll_area.pack(
        fill="both",
        expand=True,
        padx=10
    )

    song_canvas = tk.Canvas(
        scroll_area,
        bg=BG,
        highlightthickness=0
    )

    song_scrollbar = tk.Scrollbar(
        scroll_area,
        orient="vertical",
        command=song_canvas.yview
    )

    song_frame = tk.Frame(
        song_canvas,
        bg=BG
    )

    song_frame_window = song_canvas.create_window(
        (0, 0),
        window=song_frame,
        anchor="nw"
    )

    song_canvas.configure(
        yscrollcommand=song_scrollbar.set
    )

    song_scrollbar.pack(
        side="right",
        fill="y"
    )

    song_canvas.pack(
        side="left",
        fill="both",
        expand=True
    )

    def update_scroll_region(event=None):

        song_canvas.configure(
            scrollregion=song_canvas.bbox("all")
        )

    song_frame.bind(
        "<Configure>",
        update_scroll_region
    )

    def resize_song_frame(event):

        song_canvas.itemconfig(
            song_frame_window,
            width=event.width
        )

    song_canvas.bind(
        "<Configure>",
        resize_song_frame
    )

    # Mouse-wheel scrolling
    def mouse_wheel(event):

        song_canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )

    song_canvas.bind(
        "<Enter>",
        lambda event: song_canvas.bind_all(
            "<MouseWheel>",
            mouse_wheel
        )
    )

    song_canvas.bind(
        "<Leave>",
        lambda event: song_canvas.unbind_all(
            "<MouseWheel>"
        )
    )

    # ========================================================
    # SONG CARDS
    # ========================================================

    for song in songs:

        song_card = tk.Frame(
            song_frame,
            bg=SURFACE,
            padx=15,
            pady=15
        )

        song_card.pack(
            fill="x",
            pady=7,
            padx=5
        )

        # ----------------------------------------------------
        # Album cover
        # ----------------------------------------------------

        cover_url = song.get(
            "cover_url"
        )

        if cover_url:

            try:

                response = requests.get(
                    cover_url,
                    timeout=10
                )

                response.raise_for_status()

                image = Image.open(
                    BytesIO(response.content)
                )

                image = image.resize(
                    (90, 90),
                    Image.Resampling.LANCZOS
                )

                cover_image = ImageTk.PhotoImage(
                    image
                )

                cover_photo_refs.append(
                    cover_image
                )

                cover_label = tk.Label(
                    song_card,
                    image=cover_image,
                    bg=SURFACE
                )

                cover_label.pack(
                    side="left",
                    padx=(0, 18)
                )

            except Exception as error:

                print(
                    f"Cover image error for "
                    f"{song.get('title')}:",
                    error
                )

        # ----------------------------------------------------
        # Song information
        # ----------------------------------------------------

        info_frame = tk.Frame(
            song_card,
            bg=SURFACE
        )

        info_frame.pack(
            side="left",
            fill="both",
            expand=True
        )

        title_label = tk.Label(
            info_frame,
            text=song.get(
                "title",
                "Unknown song"
            ),
            bg=SURFACE,
            fg=WHITE,
            font=(TITLE_FACE, 18, "bold"),
            anchor="w"
        )

        title_label.pack(
            anchor="w"
        )

        artist_label = tk.Label(
            info_frame,
            text=song.get(
                "artist",
                "Unknown artist"
            ),
            bg=SURFACE,
            fg=MUTED,
            font=BODY_FONT,
            anchor="w"
        )

        artist_label.pack(
            anchor="w",
            pady=(3, 8)
        )

        # ----------------------------------------------------
        # Spotify button
        # ----------------------------------------------------

        spotify_url = song.get(
            "spotify_url"
        )

        if spotify_url:

            spotify_button = tk.Button(
                info_frame,
                text="▶  Play on Spotify",
                font=BUTTON_FONT,
                bg=PURPLE,
                fg=WHITE,
                activebackground=PURPLE_LIGHT,
                activeforeground=BG,
                relief="flat",
                bd=0,
                cursor="hand2",
                padx=18,
                pady=7,
                command=lambda url=spotify_url:
                    open_spotify(url)
            )

            spotify_button.pack(
                anchor="w"
            )

    vibe_footer.config(
        text=f"{len(songs)} song(s) found • scroll to explore"
    )


# ============================================================
# DEEPFACE ANALYSIS
# ============================================================

def analyze_emotion():

    try:

        # KEEPING YOUR EXISTING DEEPFACE LOGIC
        result = DeepFace.analyze(
            img_path="captured_face.jpg",
            actions=["emotion"]
        )

        emotion = result[0]["dominant_emotion"]

        show_vibe_options(
            emotion
        )

    except Exception as error:

        show_only(home_frame)

        status_label.config(
            text="DeepFace is having a moment. try again."
        )

        print(
            "DeepFace error:",
            error
        )


# ============================================================
# KEYBOARD CONTROLS
# ============================================================

def keyboard_capture(event):

    if not camera_running:
        return

    if event.keysym == "space":

        capture_photo()

    elif event.keysym.lower() == "q":

        cancel_camera()


window.bind(
    "<Key>",
    keyboard_capture
)


# ============================================================
# CLOSE APP
# ============================================================

def close_app():

    global camera_running
    global camera

    camera_running = False

    if camera is not None:

        camera.release()

    window.destroy()


window.protocol(
    "WM_DELETE_WINDOW",
    close_app
)


# ============================================================
# START
# ============================================================

show_only(home_frame)

window.mainloop()

