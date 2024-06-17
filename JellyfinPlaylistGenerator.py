import requests
import random
import json

# *** Assumptions ***
# The library is under a single user
# Movies are stored in one library (the movie pool is from one location)

# *** FIRST RUN/SETUP ***
#
# 1> Set the serverUrl to your jellyfin url (change the port if you run on a non standard port)
# 2> Create and set the API key variable apiKey:
#       Within Jellyfin: Settings > Admin Dashboard > API Keys (create one if you don't have one)
# 3> You need to get some values manually through a python console.  Set the headers variable by running the code below (line 49)
# 3> Get the userId (See code above the userId variable on how to get this value)
# 4> Get and movieID and playlistsId values (See the code below near the variables again to get the values)
# 5> Create a cron/scheduled task to run the script (usually set this to when everyone is asleep unless you are a vampire then do it during the day)




# Self exlanitory .. if you don't know this how are you using it! :D
serverUrl = "http://x.x.x.x:8096"
# Settings > Admin Dashboard > API Keys (create one if you don't have one)
apiKey = ""

# Get the user ID from GET f"{serverUrl}/Users/
#    Run the below manually (DON'T FORGET TO SET THE "headers" VARIABLE BELOW BEFORE RUNNING)
#    *******************************************************
#    url = f"{serverUrl}/Users/
#    response = requests.get(url, headers=headers)
#    movies = response.json()
#    *******************************************************
userId = ""

# Get the movies folder ID and playlist ID from GET f"{serverUrl}/Library/MediaFolders"
#    Run the below manually (DON'T FORGET TO SET THE "headers" VARIABLE BELOW BEFORE RUNNING)
#    *******************************************************
#    url = f"{serverUrl}/Library/MediaFolders"
#    response = requests.get(url, headers=headers)
#    movies = response.json()
#    *******************************************************
moviesId = ""
playlistsId = ""

# Number of movies to attempt to put in each playlist (10 seems a good number but dealers choice)
PlayListMovieNumber = 10

headers = {
    "Authorization": 'MediaBrowser Token="' + apiKey + '"'
}


def get_movies():
    url = f"{serverUrl}/Users/{userId}/Items?ParentId={moviesId}"
    response = requests.get(url, headers=headers)
    movies = response.json()
    return movies["Items"]

def get_movies_by_actor(actorName):
    url = f"{serverUrl}/Users/{userId}/Items?ParentId={moviesId}&Recursive=true&IncludeItemTypes=Movie&person={actorName}"
    response = requests.get(url, headers=headers)
    movies = response.json()
    return movies["Items"]
    

def get_playlists():
    url = f"{serverUrl}/Users/{userId}/Items?ParentId={playlistsId}"
    response = requests.get(url, headers=headers)
    playlists = response.json()
    return playlists["Items"]

def create_playlist(name):
    playlists = get_playlists()
    playlist_id = next((pl["Id"] for pl in playlists if pl["Name"] == name), None)

    if playlist_id:
        return playlist_id

    url = f"{serverUrl}/Playlists"
    data = {
        "Name": name,
        "UserId": userId,
        "MediaType": "Video"
    }
    response = requests.post(url, headers=headers, json=data)
    playlist_id = response.json()["Id"]
    return playlist_id

def update_item(item_id):
    url = f"{serverUrl}/Items/{item_id}"
    data = {
        "UserId": userId,
        "MediaType": "Video"
    }
    requests.post(url, headers=headers, json=data)

def empty_playlist(playlist_id):
    url = f"{serverUrl}/Playlists/{playlist_id}/Items?userId={userId}"
    response = requests.get(url, headers=headers)
    playlist_items = response.json()

    if len(playlist_items) == 0:
        return

    items = [str(item["PlaylistItemId"]) for item in playlist_items["Items"]]
    url = f"{serverUrl}/Playlists/{playlist_id}/Items?userId={userId}&entryIds={','.join(items)}"
    requests.delete(url, headers=headers)

def update_daily_mix(name, genre):
    url = f"{serverUrl}/Users/{userId}/Items?ParentId={moviesId}&Genres={genre}"
    response = requests.get(url, headers=headers)
    movies = response.json()
    num_of_movies_to_select = min(len(movies["Items"]), PlayListMovieNumber)

    playlist_movies = random.sample(movies["Items"], num_of_movies_to_select)

    playlist_id = create_playlist(name)
    empty_playlist(playlist_id)

    playlist_item_ids = [str(movie["Id"]) for movie in playlist_movies]
    url = f"{serverUrl}/Playlists/{playlist_id}/Items?userId={userId}&ids={','.join(playlist_item_ids)}"
    requests.post(url, headers=headers)

def update_daily_mix_decade(name, minyear, maxyear):
    url = f"{serverUrl}/Users/{userId}/Items?ParentId={moviesId}&minPremiereDate={minyear}&maxPremiereDate={maxyear}"
    response = requests.get(url, headers=headers)
    movies = response.json()
    num_of_movies_to_select = min(len(movies["Items"]), PlayListMovieNumber)

    playlist_movies = random.sample(movies["Items"], num_of_movies_to_select)

    playlist_id = create_playlist(name)
    empty_playlist(playlist_id)

    playlist_item_ids = [str(movie["Id"]) for movie in playlist_movies]
    url = f"{serverUrl}/Playlists/{playlist_id}/Items?userId={userId}&ids={','.join(playlist_item_ids)}"
    requests.post(url, headers=headers)

def update_daily_mix_actor(name, actorName):
    movies = get_movies_by_actor(actorName)
    if len(movies) == 0:
        print(f"No movies found for {actorName}")
        return
    num_of_movies_to_select = min(len(movies), PlayListMovieNumber)

    playlist_movies = random.sample(movies, num_of_movies_to_select)

    playlist_id = create_playlist(name)
    empty_playlist(playlist_id)

    playlist_item_ids = [str(movie["Id"]) for movie in playlist_movies]
    url = f"{serverUrl}/Playlists/{playlist_id}/Items?userId={userId}&ids={','.join(playlist_item_ids)}"
    requests.post(url, headers=headers)

def update_daily_mostwatched():
    playCountThreshold = 3
    url = f"{serverUrl}/Users/{userId}/Items?ParentId={moviesId}&Recursive=true&IncludeItemTypes=Movie&isplayed=true"
    response = requests.get(url, headers=headers)
    movies = response.json()

    playedMovies = []

    for movie in movies["Items"]:
        if movie["UserData"]["PlayCount"] > playCountThreshold:
            playedMovies.append(movie)

    num_of_movies_to_select = min(len(playedMovies), PlayListMovieNumber)

    playlist_movies = random.sample(playedMovies, num_of_movies_to_select)

    playlist_id = create_playlist("Daily Mix Most Watched")
    empty_playlist(playlist_id)

    playlist_item_ids = [str(movie["Id"]) for movie in playlist_movies]
    url = f"{serverUrl}/Playlists/{playlist_id}/Items?userId={userId}&ids={','.join(playlist_item_ids)}"
    requests.post(url, headers=headers)

def update_daily_neverwatched():
    url = f"{serverUrl}/Users/{userId}/Items?ParentId={moviesId}&Recursive=true&IncludeItemTypes=Movie&isplayed=false"
    response = requests.get(url, headers=headers)
    movies = response.json()
    movies = movies["Items"]

    num_of_movies_to_select = min(len(movies), PlayListMovieNumber)

    playlist_movies = random.sample(movies, num_of_movies_to_select)

    playlist_id = create_playlist("Daily Mix Not Watched")
    empty_playlist(playlist_id)
    
    playlist_item_ids = [str(movie["Id"]) for movie in playlist_movies]
    url = f"{serverUrl}/Playlists/{playlist_id}/Items?userId={userId}&ids={','.join(playlist_item_ids)}"
    requests.post(url, headers=headers)


# Genres: Action, Adventure, Animation, Comedy, Crime, Documentary, Drama, Family, Fantasy, History, Horror, Music, Mystery, Romance, Science Fiction, Thriller, TV Movie, War, Western

# Add any genres that you are interested in to the array below.  Use the genres from the above comment
genres = [
    "Comedy", "Action", "Crime", "Fantasy", 
    "Science Fiction", "Thriller", "Adventure", 
    "Mystery", "Romance"
]

# Update playlist for each genre selected
for genre in genres:
    update_daily_mix(f"Daily Mix {genre}", genre)

# Update some decade playlists
update_daily_mix_decade(f"Daily Mix 1980s", "1980-01-01", "1989-12-31")
update_daily_mix_decade(f"Daily Mix 1990s", "1990-01-01", "1999-12-31")
update_daily_mix_decade(f"Daily Mix 2000s", "2000-01-01", "2009-12-31")

# Update actor specific playlists
update_daily_mix_actor("Daily Mix The Sandler", "Adam Sandler")

# Most watched and never watched playlists
update_daily_mostwatched()
update_daily_neverwatched()
