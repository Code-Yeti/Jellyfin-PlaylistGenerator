*** FIRST RUN/SETUP ***

1> Set the serverUrl to your jellyfin url (change the port if you run on a non standard port)

2> Create and set the API key variable apiKey:
    Within Jellyfin: Settings > Admin Dashboard > API Keys (create one if you don't have one)
      
3> You need to get some values manually through a python console.  Set the headers variable by running the code below (line 49)

3> Get the userId (See code above the userId variable on how to get this value)

4> Get and movieID and playlistsId values (See the code below near the variables again to get the values)

5> Create a cron/scheduled task to run the script (usually set this to when everyone is asleep unless you are a vampire then do it during the day)
