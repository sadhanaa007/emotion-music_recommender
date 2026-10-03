import os
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_spotify_token():
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET),
    )

    response.raise_for_status()
    return response.json()["access_token"]


def find_spotify_info(title, artist, token):
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
        return None, None

    track = tracks[0]

    spotify_url = track["external_urls"]["spotify"]

    cover_url = None

    if track.get("album") and track["album"].get("images"):
        cover_url = track["album"]["images"][0]["url"]

    return spotify_url, cover_url


print("Getting Spotify access token...")

token = get_spotify_token()

print("Spotify connected!")

songs = (
    supabase
    .table("songs")
    .select("id,title,artist,spotify_url,cover_url")
    .execute()
)

print(f"Total songs: {len(songs.data)}")

for song in songs.data:

    title = song["title"]
    artist = song["artist"]

    # Only process songs that are missing either URL
    # or cover art.
    if song.get("spotify_url") and song.get("cover_url"):
        continue

    print(f"\nSearching: {title} — {artist}")

    try:
        spotify_url, cover_url = find_spotify_info(
            title,
            artist,
            token
        )

        if spotify_url:

            update_data = {
                "spotify_url": spotify_url,
                "cover_url": cover_url
            }

            supabase.table("songs").update(
                update_data
            ).eq("id", song["id"]).execute()

            print("FOUND Spotify URL")
            print("FOUND Cover URL")

        else:
            print("NOT FOUND")

    except Exception as e:
        print("ERROR:", e)


print("\nFinished!")