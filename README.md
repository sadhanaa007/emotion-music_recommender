# NIGHT FURY 🎵
### Emotion-Based Music Recommendation System

NIGHT FURY is a Python-based desktop application that detects facial emotions and recommends music based on the vibe selected by the user.

## Features
- Facial emotion detection using DeepFace.
- Webcam access using OpenCV.
- Vibe selection based on detected emotions.
- Song retrieval from a Supabase database.
- Display of song titles, artists and cover images.
- Spotify links to access recommended songs.

## Technologies Used
- Python
- Tkinter
- OpenCV
- DeepFace
- Supabase
- Pillow

## How It Works
1. The application captures an image through the webcam.
2. DeepFace analyses the image and detects the dominant emotion.
3. The user selects a preferred vibe.
4. Matching songs are retrieved from the Supabase database.
5. The recommended songs are displayed with their details and Spotify links.

## Database

The project uses a Supabase table named `songs`, containing:

| Column | Description |
|---|---|
| `title` | Song name |
| `artist` | Artist name |
| `language` | Song language |
| `vibe` | Song category |
| `spotify_url` | Spotify link |
| `cover_url` | Album cover image URL |

## Installation and Execution

**1. Clone the repository**

```bash
git clone https://github.com/sadhanaa007/emotion-music_recommender.git
cd emotion-music_recommender
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Configure Supabase**

Create a `.env` file in the project directory:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_key
```

**4. Run the application**

```bash
python main_2000s.py
```

## Future Improvements
- User profiles and listening history.
- Improved music recommendations.
- Web and mobile application support.
