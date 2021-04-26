from lyricFinder import LyricFinder
from nltk.tokenize import RegexpTokenizer
import nltk.translate.gleu_score as gleu
import numpy as np
import random
import nltk

class LyricGenerator:
    def __init__(self, artist_name:str):
        #initialize nltk variables
        self.artist_name = artist_name
        self.cmu_dict = nltk.corpus.cmudict.dict()
        self.ps = nltk.stem.PorterStemmer()
        self.tokenizer = RegexpTokenizer(r"[\w'-]+|\$[\d\.]+|,")
    
    def train(self, lyrics:dict):
        #combines all lyrics from dict into one string
        lyrics_str = '\n'.join(x['lyrics'] for x in lyrics).lower()
        #creates an list where each number in the list is the amount of stanzas in the respective song
        stanza_line_counts = [x.count("\n") + 1 for x in lyrics_str.split("\n\n")]
        
        a = np.array(stanza_line_counts)
        self.avg_stanza_len = [round(np.percentile(a,40)), round(np.percentile(a,60))]
        self.avg_stanza_count = max( round( len(stanza_line_counts) / len(lyrics) ), 1)

        lyric_tokens = self.tokenizer.tokenize(lyrics_str)
        self.get_rhymes(lyric_tokens)
        self.syll_counts = self.get_range_syllables_line(lyrics_str)

    def generate(self)->str:
        lines = []
        #loop as many times as the artist has stanzas in their songs on average
        for _ in range(self.avg_stanza_count):
            stanza = []
            temp_rhymes = list(self.rhymes)
            #choose a random length for each stanzas within 20% of the median length
            stanza_len = max(random.randint(self.avg_stanza_len[0],self.avg_stanza_len[1]), 1)
            for _ in range(max(stanza_len // 2,1)):
                #select a random rhyme from the list of rhymes and create two rhyming sentences
                rhyme = random.choice(temp_rhymes)
                temp_rhymes.remove(rhyme)
                stanza.append(self.get_rhyme_line(rhyme))
                stanza.append(self.get_rhyme_line(rhyme))
            #randomize the order of the lines of the stanza and add to the result
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
        #represents all of the words in the source lyrics that are also in cmu
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
        
        # Remove all rhyming sets with 2 or fewer words.
        for each in reverseDict.values() :
            if len(each) < 3:
                for every in each :
                    inter.remove(every)
        self.rhymes = inter
        self.word_rhymes = forwardDict
        self.word_rhymes_reverse = reverseDict

    def get_rhyme_line(self, rhyme):
        #get a list of all words in the dict that rhyme with the word
        listRhyming = self.word_rhymes_reverse[self.word_rhymes[rhyme]]
        if len(listRhyming) == 0 :
            return 0
        #choose a random rhyme and create sentence from that
        rhymeWord = random.choice(listRhyming)
        newLine = self.generate_model(self.invertedCfd, rhymeWord)
        newLine.reverse()
        return ' '.join(newLine)
                
    def generate_model(self, cfdist, word) :
        result = []
        tempWord = ""
        #randomize length of the line from all syllable patterns in the source
        num = random.choice(self.syll_counts)
        count = 0
        while count <= num :
            #detect if a token is a contraction or comma and add it to the end of the previous word
            if word[0] in [',',"'"]:
                tempWord = word
            else:
                result.append(word + tempWord)
                tempWord = ""
                #adjust the count to the current length of the sentence in syllables
                count += sum(self.get_range_syllables_line(word)[:1])

            possible = cfdist[word].keys()
            possible = list( possible )
            if len(possible) == 0 :
                return result
            # Find a random word from the most probable words
            topOfRange = int(len(possible)*.5)
            word = possible[random.randint(0,topOfRange)]
        result[-1] = result[-1] + tempWord
        return result

    def analyze_lyrics(self, ref_lyric_data, hyp_lyrics):
        #create list of reference lyrics for gleu
        ref_list = [self.tokenizer.tokenize(x['lyrics']) for x in ref_lyric_data]
        #create a hypothesis lyric
        hyp = self.tokenizer.tokenize(hyp_lyrics)
        #calculate GLEU for the hypothesis lyrics
        result = gleu.sentence_gleu(ref_list,hyp)
        return result

    def get_range_syllables_line(self, raw_text:list):
        #keeps track of all of the syllable counts
        syll_counts = []

        punctuation = [ '!', '#', '$', '%', '&', '(', ')', '*',
        '+', ',', '-', '.', '/', ':', ';', '<', '=', '>', '?',
        '@', '[', "\\", "]", "^", "_", "`", "{", "|", "}", "~" ]
        vowels = 'aeiouAEIOU'
        

        #splits raw text into lines
        for line in raw_text.split('\n'):
            #splits line into tokens
            count = 0
            tokens = self.tokenizer.tokenize(line)
            for each in tokens:
                each = each.lower()
                #makes sure each token is not punctuation, try to look up token in cmu dictionary
                if each not in punctuation:
                    try:
                        l = self.cmu_dict[each]
                        first = l[0]
                        for each in first:
                            if each[0] in vowels:
                                # if has a vowel in cmu, it counts as a syllable
                                count = count + 1
                    except Exception:
                        #if token is not in cmu, try to lookup its stem
                        s = self.ps.stem(each)
                        try:
                            x = self.cmu_dict[s]
                            f = x[0]
                            for each_ in f:
                                if each_[0] in vowels:
                                    count = count + 1
                        except Exception:
                            #if stem isn't in the dictionary either, count the token as 1 syllable
                            count = count + 1
            if (count != 0):
                syll_counts.append(count)

        return syll_counts
        #get a random value from that list later when generating lyrics

def main():
    genius_token = 'Pi4k_2PC5BmgU-WQorbpVE-3AWtCNGiD0szQMkfBb8pqEAEPRiR6-_lWmahaxxIn'
    lf = LyricFinder(genius_token, 'lyrics')

    artists = ['The Beatles', 'King Gizzard', 'Justin Bieber', 'Animal Collective', 'Eminem', 'Led Zeppelin', 'Luke Combs', 'Pitbull', 'Kendrick Lamar', 'Maluma']
    song_counts = [5,20,50]

    lines = []
    for count in song_counts:
        artists = lf.get_artists_lyrics(artists,count)
        for artist in artists:
            data = artists[artist]
            gen = LyricGenerator(artist)
            gen.train(data)
            lyrics = gen.generate()
            lyrics_print = lyrics.replace("\n","\\n")
            gleu_score = gen.analyze_lyrics(data,lyrics)
            line = "Artist: %s, Number of songs: %d, Score: %f - Lyrics: %s" % (artist, count, gleu_score, lyrics_print)
            lines.append(line)
            print(line + '\n')
    with open("tests-results.txt",'w') as f:
        f.writelines(lines)
        
if __name__ == "__main__":
    main()
