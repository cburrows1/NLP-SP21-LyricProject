from lyricFinder import LyricFinder
from nltk.tokenize import RegexpTokenizer
import nltk.translate.gleu_score as gleu
import numpy as np
import random
import nltk

class LyricGenerator:
    def __init__(self, artist_name:str):
        self.artist_name = artist_name
        self.cmu_dict = nltk.corpus.cmudict.dict()
        self.tokenizer = RegexpTokenizer(r"[\w'-]+|\$[\d\.]+|,")
    
    def train(self, lyrics:dict):
        lyrics_str = '\n'.join(x['lyrics'] for x in lyrics).lower()
        stanza_line_counts = [x.count("\n") + 1 for x in lyrics_str.split("\n\n")]
        
        a = np.array(stanza_line_counts)
        self.avg_stanza_len = [round(np.percentile(a,40)), round(np.percentile(a,60))]
        self.avg_stanza_count = round( len(stanza_line_counts) / len(lyrics) )

        lyric_tokens = self.tokenizer.tokenize(lyrics_str)
        self.get_rhymes(lyric_tokens)
        self.get_range_syllables_line(lyrics_str)

    def generate(self)->str:
        lines = []
        for _ in range(self.avg_stanza_count):
            stanza = []
            temp_rhymes = list(self.rhymes)
            stanza_len = random.randint(self.avg_stanza_len[0],self.avg_stanza_len[1])
            for _ in range(stanza_len // 2):
                rhyme = random.choice(temp_rhymes)
                temp_rhymes.remove(rhyme)
                stanza.append(self.get_rhyme_line(rhyme))
                stanza.append(self.get_rhyme_line(rhyme))
            random.shuffle(stanza)
            lines += stanza
            lines.append("")
        result = '\n'.join(lines)
        return result
        
    def get_rhymes(self, text:list):
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
        tempWord = ""
        vowels = set('aeiouAEIOU')

        num = random.choice(self.syll_counts)
        count = 0
        while count <= num :
            if word[0] in [',',"'"]:
                tempWord = word
            else:
                result.append(word + tempWord)
                tempWord = ""
                for letter in word:
                    if letter in vowels:
                        count = count + 1
            possible = cfdist[word].keys()
            possible = list( possible )
            if len(possible) == 0 :
                return result
            # Find a random word from the most probable words
            topOfRange = int(len(possible)*.2)
            word = possible[random.randint(0,topOfRange)]
        result[-1] = result[-1] + tempWord
        return result

    def analyze_lyrics(self, ref_lyric_data, hyp_lyrics):
        ref_list = [self.tokenizer.tokenize(x['lyrics']) for x in ref_lyric_data]
        hyp = self.tokenizer.tokenize(hyp_lyrics)
        result = gleu.sentence_gleu(ref_list,hyp)
        return result

    def get_range_syllables_line(self, raw_text:list):
        #keeps track of all of the syllable counts
        syll_counts = []

        d = nltk.corpus.cmudict.dict()
        punctuation = ['!','#','$','%','&','(',')','*','+', ',', '-', '.', '/', ':', ';', '<', '=', '>', '?', '@', '[', "\\", "]", "^", "_", "`", "{", "|", "}", "~"]
        vowels = 'aeiouAEIOU'
        ps = nltk.stem.PorterStemmer()

        #splits raw text into lines
        for line in raw_text.split('\n'):
            #splits line into tokens
            #print(line)
            count = 0
            tokens = self.tokenizer.tokenize(line)
            for each in tokens:
                #print(each)
                each = each.lower()
                #makes sure each token is not punctuation, try to look up token in cmu dictionary
                if each not in punctuation:
                    try:
                        l = d[each]
                        first = l[0]
                        for each in first:
                            if each[0] in vowels:
                                # if has a vowel in cmu, it counts as a syllable
                                count = count + 1
                    except Exception:
                        #if token is not in cmu, try to lookup its stem
                        s = ps.stem(each)
                        try:
                            x = d[s]
                            f = x[0]
                            for each_ in f:
                                if each_[0] in vowels:
                                    count = count + 1
                        except Exception:
                            #if stem isn't in the dictionary either, count the token as 1 syllable
                            count = count + 1
            #print(count)
            if (count != 0):
                syll_counts.append(count)

        self.syll_counts = syll_counts
        #get a random value from that list later when generating lyrics

def main():
    genius_token = 'Pi4k_2PC5BmgU-WQorbpVE-3AWtCNGiD0szQMkfBb8pqEAEPRiR6-_lWmahaxxIn'
    lf = LyricFinder(genius_token, 'lyrics')

    artist = 'The Beatles'
    data = lf.get_artist_lyrics(artist, num_songs=100)

    gen = LyricGenerator(artist)
    gen.train(data)
    lyrics = gen.generate()
    
    print(lyrics)
    print(gen.analyze_lyrics(data,lyrics))

if __name__ == "__main__":
    main()
