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

* Run lyricGenerator.py to test lyric retrieval and generation
  * Use CLI arguments artist and song_count to set the parameters of selected lyrics for the generation
    * If no CLI arguments are provided defaults will be used (The Beatles with 10 songs)
* Run function test() in lyricGenerator.py to test GLEU across many artists
* Use lyricFinder.py if only the datasets are needed