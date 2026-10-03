import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)


def get_songs_by_vibe(vibe):
    response = (
        supabase
        .table("songs")
        .select("*")
        .eq("vibe", vibe)
        .execute()
    )

    return response.data


songs = get_songs_by_vibe("calm")

print("Calm songs:")
print(songs)