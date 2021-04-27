# NLP-SP21-LyricProject
**Cameron Burrows, Kara Evans**
## Description
* Natural Language Processing project that can find any artists songs and lyrics from https://genius.com
* Stores retrieved lyrics for faster subsequent processing
* Generates original lyrics for the given artist using their selected songs
## Dependencies
Use pip to install these dependencies if they arent already installed
* numpy
* lyricsgenius
* nltk

## Usage
* We have left our genius token in the code for ease of testing, however this could be replaced with your own token obtained from [genius](https://genius.com/api-clients)
* Run lyricGenerator.py to test lyric retrieval and generation
  * Use CLI arguments artist and song_count to set the parameters of selected lyrics for the generation
    * ex. python lyricGenerator.py --artist "The Beatles" --song_count 15
  * If no CLI arguments are provided defaults will be used (The Beatles with 10 songs)
    * There is no Beatles 10 file, so on first execution the songs will be requested, but on subsequent runs they will be read from file.
* Run function test() in lyricGenerator.py to test GLEU across many artists
  * By default main() will run which checks the CLI arguments and generates one set of results
  * Uncomment test() in \_\_main\_\_ if you'd like to run the tests instead
  * The required json files to run the tests are included in /lyrics/ so there should not be any network load for running tests
* Use lyricFinder.py if only the datasets are needed