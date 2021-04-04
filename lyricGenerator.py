from lyricFinder import LyricFinder
import nltk

class LyricGenerator:
    def __init__(self, artist_name:str):
        self.artist_name = artist_name
    
    def train(self, lyrics:dict):
        pass

    def generate(self, num_lines:int)->str:
        return "TODO"


def main():
    genius_token = 'Pi4k_2PC5BmgU-WQorbpVE-3AWtCNGiD0szQMkfBb8pqEAEPRiR6-_lWmahaxxIn'
    lf = LyricFinder(genius_token, 'lyrics')

    artist = 'The Beatles'
    data = lf.get_artist_lyrics(artist, num_songs=100)

    gen = LyricGenerator(artist)
    gen.train(data)
    lyrics = gen.generate(10)

    print(lyrics)

if __name__ == "__main__":
    main()
