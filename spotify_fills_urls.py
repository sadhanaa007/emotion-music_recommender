import os
import requests

from dotenv import load_dotenv
from supabase import create_client


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


# ============================================================
# CONNECT TO SUPABASE
# ============================================================

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# ============================================================
# GET SPOTIFY ACCESS TOKEN
# ============================================================

def get_spotify_token():

    print("Getting Spotify access token...")

    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "client_credentials"
        },
        auth=(
            SPOTIFY_CLIENT_ID,
            SPOTIFY_CLIENT_SECRET
        )
    )

    response.raise_for_status()

    token = response.json()["access_token"]

    print("Spotify connected!")

    return token


# ============================================================
# SEARCH SPOTIFY
# ============================================================

def search_spotify(title, artist, token):

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Search using both title and artist.
    query = f'track:"{title}" artist:"{artist}"'

    response = requests.get(
        "https://api.spotify.com/v1/search",
        headers=headers,
        params={
            "q": query,
            "type": "track",
            "limit": 5,
            "market": "IN"
        }
    )

    response.raise_for_status()

    tracks = response.json().get(
        "tracks",
        {}
    ).get(
        "items",
        []
    )

    if not tracks:

        # Fallback search if the strict search fails.
        fallback_query = f"{title} {artist}"

        response = requests.get(
            "https://api.spotify.com/v1/search",
            headers=headers,
            params={
                "q": fallback_query,
                "type": "track",
                "limit": 5,
                "market": "IN"
            }
        )

        response.raise_for_status()

        tracks = response.json().get(
            "tracks",
            {}
        ).get(
            "items",
            []
        )

    if not tracks:
        return None

    # Use the first result.
    track = tracks[0]

    spotify_url = (
        track
        .get("external_urls", {})
        .get("spotify")
    )

    cover_url = None

    album = track.get(
        "album",
        {}
    )

    images = album.get(
        "images",
        []
    )

    if images:
        cover_url = images[0].get("url")

    return {
        "spotify_url": spotify_url,
        "cover_url": cover_url
    }


# ============================================================
# MAIN
# ============================================================

def main():

    token = get_spotify_token()

    # Get all songs.
    response = (
        supabase
        .table("songs")
        .select("*")
        .execute()
    )

    songs = response.data

    print(
        f"Total songs: {len(songs)}"
    )

    print("=" * 60)

    updated_count = 0
    skipped_count = 0
    failed_count = 0

    for song in songs:

        song_id = song.get("id")
        title = song.get("title")
        artist = song.get("artist")

        print()
        print(
            f"Searching: {title} — {artist}"
        )

        # ----------------------------------------------------
        # IMPORTANT:
        # Don't overwrite URLs that you already entered manually.
        # ----------------------------------------------------

        current_spotify_url = song.get(
            "spotify_url"
        )

        current_cover_url = song.get(
            "cover_url"
        )

        try:

            result = search_spotify(
                title,
                artist,
                token
            )

            if not result:

                print("NOT FOUND")
                failed_count += 1
                continue

            update_data = {}

            # Only fill missing Spotify URL.
            if (
                not current_spotify_url
                and result.get("spotify_url")
            ):

                update_data["spotify_url"] = (
                    result["spotify_url"]
                )

                print(
                    "FOUND Spotify URL"
                )

            else:

                print(
                    "Spotify URL already exists — keeping it"
                )

            # Only fill missing cover.
            if (
                not current_cover_url
                and result.get("cover_url")
            ):

                update_data["cover_url"] = (
                    result["cover_url"]
                )

                print(
                    "FOUND Cover URL"
                )

            else:

                print(
                    "Cover URL already exists — keeping it"
                )

            # ------------------------------------------------
            # THIS IS THE IMPORTANT PART
            # ACTUALLY UPDATE SUPABASE
            # ------------------------------------------------

            if update_data:

                update_response = (
    supabase
    .table("songs")
    .update(update_data)
    .eq("id", song_id)
    .select()
    .execute()
)

                # Verify that Supabase returned the updated row.
                if update_response.data:

                    print(
                        "✓ SAVED TO SUPABASE"
                    )

                    updated_count += 1

                else:

                    print(
                        "⚠ Update sent, but no updated row returned"
                    )

            else:

                skipped_count += 1

        except Exception as error:

            print(
                f"ERROR: {error}"
            )

            failed_count += 1

    print()
    print("=" * 60)
    print("FINISHED")
    print("=" * 60)

    print(
        f"Updated: {updated_count}"
    )

    print(
        f"Skipped: {skipped_count}"
    )

    print(
        f"Failed/Not found: {failed_count}"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()