import os
import re
import time
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
        ),
        timeout=30
    )

    response.raise_for_status()

    token = response.json()["access_token"]

    print("Spotify connected!")

    return token


# ============================================================
# EXTRACT TRACK ID FROM SPOTIFY URL
# ============================================================

def extract_track_id(spotify_url):

    if not spotify_url:
        return None

    # Handles:
    # https://open.spotify.com/track/TRACK_ID
    # https://open.spotify.com/track/TRACK_ID?si=xxxx

    match = re.search(
        r"open\.spotify\.com/track/([A-Za-z0-9]+)",
        spotify_url
    )

    if match:
        return match.group(1)

    return None


# ============================================================
# GET COVER FROM EXACT SPOTIFY TRACK
# ============================================================

def get_cover_url(track_id, token):

    headers = {
        "Authorization": f"Bearer {token}"
    }

    url = f"https://api.spotify.com/v1/tracks/{track_id}"

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    # --------------------------------------------------------
    # RATE LIMIT
    # --------------------------------------------------------

    if response.status_code == 429:

        retry_after = response.headers.get(
            "Retry-After",
            "unknown"
        )

        print()
        print("⚠ Spotify rate limit reached.")
        print(f"Spotify says Retry-After: {retry_after}")
        print("Stopping safely.")
        print()

        return "RATE_LIMIT"


    # --------------------------------------------------------
    # OTHER ERRORS
    # --------------------------------------------------------

    if response.status_code != 200:

        print(
            f"Spotify returned HTTP {response.status_code}"
        )

        return None


    # --------------------------------------------------------
    # GET ALBUM COVER
    # --------------------------------------------------------

    track = response.json()

    album = track.get(
        "album",
        {}
    )

    images = album.get(
        "images",
        []
    )

    if not images:

        return None

    # Spotify normally gives multiple sizes.
    # First image is usually the largest.

    cover_url = images[0].get("url")

    return cover_url


# ============================================================
# MAIN
# ============================================================

def main():

    token = get_spotify_token()

    print()
    print("Getting songs from Supabase...")
    print()

    response = (
        supabase
        .table("songs")
        .select("*")
        .execute()
    )

    songs = response.data

    print(
        f"Total database rows: {len(songs)}"
    )

    print("=" * 60)

    # --------------------------------------------------------
    # Only songs that:
    #
    # 1. HAVE a Spotify URL
    # 2. DON'T have a cover URL yet
    #
    # --------------------------------------------------------

    incomplete_songs = [
        song
        for song in songs
        if song.get("spotify_url")
        and not song.get("cover_url")
    ]

    print(
        f"Songs needing covers: {len(incomplete_songs)}"
    )

    print("=" * 60)

    updated_count = 0
    skipped_count = 0
    failed_count = 0

    # ========================================================
    # PROCESS SONGS
    # ========================================================

    for index, song in enumerate(
        incomplete_songs,
        start=1
    ):

        song_id = song.get("id")

        title = song.get(
            "title",
            "Unknown"
        )

        artist = song.get(
            "artist",
            "Unknown"
        )

        spotify_url = song.get(
            "spotify_url"
        )

        print()
        print(
            f"[{index}/{len(incomplete_songs)}]"
        )

        print(
            f"{title} — {artist}"
        )

        # ----------------------------------------------------
        # EXTRACT TRACK ID
        # ----------------------------------------------------

        track_id = extract_track_id(
            spotify_url
        )

        if not track_id:

            print(
                "⚠ Could not extract Spotify track ID."
            )

            failed_count += 1
            continue

        print(
            f"Track ID: {track_id}"
        )

        # ----------------------------------------------------
        # GET COVER
        # ----------------------------------------------------

        try:

            cover_url = get_cover_url(
                track_id,
                token
            )

            # ------------------------------------------------
            # RATE LIMIT
            # ------------------------------------------------

            if cover_url == "RATE_LIMIT":

                print()
                print(
                    "============================================================"
                )
                print(
                    "STOPPED DUE TO SPOTIFY RATE LIMIT"
                )
                print(
                    "============================================================"
                )

                break

            # ------------------------------------------------
            # NOT FOUND
            # ------------------------------------------------

            if not cover_url:

                print(
                    "⚠ No cover found."
                )

                failed_count += 1
                continue

            # ------------------------------------------------
            # SAVE TO SUPABASE
            # ------------------------------------------------

            update_response = (
                supabase
                .table("songs")
                .update({
                    "cover_url": cover_url
                })
                .eq(
                    "id",
                    song_id
                )
                .select()
                .execute()
            )

            if update_response.data:

                print(
                    "✓ Cover URL saved to Supabase"
                )

                updated_count += 1

            else:

                print(
                    "⚠ Cover found but Supabase update returned no row."
                )

                failed_count += 1

            # ------------------------------------------------
            # SMALL DELAY
            #
            # Don't hammer Spotify.
            # ------------------------------------------------

            time.sleep(1)

        except Exception as error:

            print(
                f"ERROR: {error}"
            )

            failed_count += 1


    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print()
    print("=" * 60)
    print("FINISHED")
    print("=" * 60)

    print(
        f"Database rows: {len(songs)}"
    )

    print(
        f"Songs needing covers at start: {len(incomplete_songs)}"
    )

    print(
        f"Cover URLs updated: {updated_count}"
    )

    print(
        f"Failed: {failed_count}"
    )

    print(
        f"Skipped: {skipped_count}"
    )

    print("=" * 60)

    print()
    print(
        "Any successfully saved cover URLs are safe in Supabase."
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()