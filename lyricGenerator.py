from lyricFinder import LyricFinder
import random
import nltk

class LyricGenerator:
    def __init__(self, artist_name:str):
        self.artist_name = artist_name
        self.cmu_dict = nltk.corpus.cmudict.dict()
    
    def train(self, lyrics:dict):
        lyrics = '\n'.join(x['lyrics'] for x in lyrics)
        self.get_rhymes(lyrics)

    def generate(self, num_lines:int)->str:
        rhymes = random.choices(list(self.rhymes),k=round(num_lines/2))
        lines = []
        for rhyme in rhymes:
            lines.append(self.get_rhyme_line(rhyme))
            lines.append(self.get_rhyme_line(rhyme))
        #random.shuffle(lines)
        result = '\n'.join(lines)
        return result
        
    def get_rhymes(self, raw_text:str):
        text = nltk.word_tokenize(raw_text)
        vocab = set(text)
        bgrams = list(nltk.bigrams(text))
        invertedBigrams = [([pair[1], pair[0]]) for pair in bgrams]
        self.invertedCfd = nltk.ConditionalFreqDist(invertedBigrams)
        inter = vocab.intersection(self.cmu_dict.keys())
        
        forwardDict = dict()
        reverseDict = dict()
        for each in inter :
            pron = self.cmu_dict[each]
            #rhyming part
            temp = ''.join(pron[0][1:])
            forwardDict[each] = temp
            if temp in reverseDict :
                reverseDict[temp].append(each)
            else :
                reverseDict[temp] = [each]
        
        # Remove all rhyming sets with 3 or fewer words.
        for each in reverseDict.values() :
            if len(each) < 4:
                for every in each :
                    inter.remove(every)
        self.rhymes = inter
        self.word_rhymes = forwardDict
        self.word_rhymes_reverse = reverseDict

    def get_rhyme_line(self, rhyme, min_words=10):
        result = 0
        while result < min_words :
            listRhyming = self.word_rhymes_reverse[self.word_rhymes[rhyme]]
            if len(listRhyming) == 0 :
                return 0
            rhymeWord = random.choice(listRhyming)
            newLine = self.generate_model(self.invertedCfd, rhymeWord, min_words)
            newLine.reverse()
            result = len(newLine)
        return ' '.join(newLine)
                
    def generate_model(self, cfdist, word, num) :
        result = []
        for i in range(num) :
            # Make sure it's not <most> punctuation
            if word[0] < 'A' or word[0] > 'z' :
                i = i - 1
            else :
                result.append(word)
            possible = cfdist[word].keys()
            possible = list( possible )
            if len(possible) == 0 :
                return result
            # Find a random word from the most probable words
            topOfRange = int(len(possible)*.2)
            word = possible[random.randint(0,topOfRange)]
                
        return result


def main():
    #TODO-
    #   make rhymes more accurate - make it actually recognize rhyming lines - good
    #   pos tagging for sentence structure - remove
    #   line/song length - good
    #   sentiment analysis - remove
    #   find syllables of every lines - add
    #   improve accuracy numbers - GLEU https://www.linkedin.com/pulse/quality-machine-translation-alternatives-bleu-score-ilya-butenko/   


    genius_token = 'Pi4k_2PC5BmgU-WQorbpVE-3AWtCNGiD0szQMkfBb8pqEAEPRiR6-_lWmahaxxIn'
    lf = LyricFinder(genius_token, 'lyrics')

    artist = 'The Beatles'
    data = lf.get_artist_lyrics(artist, num_songs=7)

    gen = LyricGenerator(artist)
    gen.train(data)
    lyrics = gen.generate(10)

    print(lyrics)

if __name__ == "__main__":
    main()
