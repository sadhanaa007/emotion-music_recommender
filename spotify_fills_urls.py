import os
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# -----------------------------
# Spotify credentials
# -----------------------------
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# -----------------------------
# Supabase credentials
# -----------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# -----------------------------
# Get Spotify access token
# -----------------------------
def get_spotify_token():
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET),
    )

    response.raise_for_status()
    return response.json()["access_token"]


# -----------------------------
# Search Spotify for a song
# -----------------------------
def find_spotify_url(title, artist, token):
    headers = {
        "Authorization": f"Bearer {token}"
    }

    query = f'track:"{title}" artist:"{artist}"'

    response = requests.get(
        "https://api.spotify.com/v1/search",
        headers=headers,
        params={
            "q": query,
            "type": "track",
            "limit": 1
        }
    )

    response.raise_for_status()

    tracks = response.json()["tracks"]["items"]

    if not tracks:
        return None

    return tracks[0]["external_urls"]["spotify"]


# -----------------------------
# Main
# -----------------------------
print("Getting Spotify access token...")

token = get_spotify_token()

print("Spotify connected!")

songs = (
    supabase
    .table("songs")
    .select("id,title,artist,spotify_url")
    .is_("spotify_url", "null")
    .execute()
)

print(f"Songs without Spotify URLs: {len(songs.data)}")

for song in songs.data:

    title = song["title"]
    artist = song["artist"]

    print(f"\nSearching: {title} — {artist}")

    try:
        spotify_url = find_spotify_url(title, artist, token)

        if spotify_url:
            supabase.table("songs").update(
                {"spotify_url": spotify_url}
            ).eq("id", song["id"]).execute()

            print("FOUND:", spotify_url)

        else:
            print("NOT FOUND")

    except Exception as e:
        print("ERROR:", e)


print("\nFinished!")