import nltk
import numpy
from pymongo import MongoClient



connection = MongoClient('mongodb://localhost:27017/Culminate')
db = connection.Culminate
# nltk.downloader.download('maxent_ne_chunker')
# nltk.downloader.download('words')
# nltk.downloader.download('treebank')
# nltk.downloader.download('maxent_treebank_pos_tagger')
# nltk.downloader.download('punkt')



class tags():
    def __init__(self, text=None):
        if not text:
            raise Exception('Text is required')

    def getCountry(text):

        text = nltk.word_tokenize(text)
        nes = nltk.ne_chunk(nltk.pos_tag(text))
        places = []
        for ne in nes:
            print(type(ne))
            if type(ne) is nltk.tree.Tree:
                if (ne.label() == 'GPE' or ne.label() == 'PERSON' or ne.label() == 'ORGANIZATION'):
                    places.append(u' '.join([i[0] for i in ne.leaves()]))
        places = set(places)
        for place in places:
            
