import os, json
from lyricsgenius import Genius


class LyricFinder:
    def __init__(self, genius_key:str, save_path:str):
        self.genius = Genius(genius_key)

        #lyrics genius settings
        self.genius.verbose = True
        self.genius.remove_section_headers = True
        self.genius.skip_non_songs = True
        
        self.path = save_path
        self.all_lyrics = {}

    def get_artist_lyrics(self, artist_name:str, num_songs=50, overwrite=False)->list:
        #creates string path for where to save and read file
        artist_path = os.path.join(self.path,"{0}_{1}.json".format(artist_name.lower().replace(' ','_'), num_songs))
        #if the lyrics are already cached in a named file return that
        if os.path.exists(artist_path) and not overwrite:
            with open(artist_path,'r') as f:
                lyrics = json.load(f)
            self.all_lyrics[artist_name] = lyrics
            return lyrics

        #search the artists page using genius until the requested amount of songs are found
        while True:
                try:
                    artist = self.genius.search_artist(artist_name, max_songs=1)
                    break
                except:
                    pass
        page = 1
        songs = []
        while page and len(songs) < num_songs:
            request = self.genius.artist_songs(artist.id,
                                        sort='popularity',
                                        per_page=50,
                                        page=page,
                                        )
            songs.extend(request['songs'])
            page = request['next_page']
        songs = songs[:num_songs]
        
        #go through each song and request the lyrics
        lyrics = []
        for song in songs:
            while True:
                try:
                    genius_song = self.genius.search_song(song['title'], artist.name)
                    break
                except:
                    pass
            if genius_song is None:
                continue
            lyrics.append({'title':song['title'], 'lyrics':genius_song.lyrics})
        self.all_lyrics[artist_name] = lyrics

        #save the lyrics in a file
        artist_path = os.path.join(self.path,"{0}_{1}.json".format(artist_name.lower().replace(' ','_'), len(lyrics)))
        with open(artist_path,'w') as f:
            json.dump(lyrics, f, sort_keys=True, indent=4, separators=(',', ': '))
        return lyrics

    #returns a collection of artists lyrics
    def get_artists_lyrics(self, artist_names:str, songs_each)->dict:
        return {artist:self.get_artist_lyrics(artist, songs_each, overwrite=False) for artist in artist_names}
            

def main():

    #go here['https://genius.com/api-clients'] to get ur token
    genius_token = 'Pi4k_2PC5BmgU-WQorbpVE-3AWtCNGiD0szQMkfBb8pqEAEPRiR6-_lWmahaxxIn'
    lf = LyricFinder(genius_token, 'lyrics')

    artists = ['The Beatles', 'King Gizzard', 'Pixies', 'Kanye West', 'of Montreal']

    print(lf.get_artists_lyrics(artists,10))
    print(lf.all_lyrics)

if __name__ == '__main__':
    main()