import nltk
from pymongo import MongoClient
from pprint import pprint

connection = MongoClient('mongodb://localhost:27017/Culminate')
db = connection.Culminate


# nltk.downloader.download('maxent_ne_chunker')
# nltk.downloader.download('words')
# nltk.downloader.download('treebank')
# nltk.downloader.download('maxent_treebank_pos_tagger')
# nltk.downloader.download('punkt')
# nltk.download('averaged_perceptron_tagger')



class tags():
    def __init__(self, text=None):
        if not text:
            raise Exception('Text is required')

    def getCountry(text):

        text = nltk.word_tokenize(text)
        nes = nltk.ne_chunk(nltk.pos_tag(text))
        places = []
        for ne in nes:
            if type(ne) is nltk.tree.Tree:
                if (ne.label() == 'GPE' or ne.label() == 'PERSON'):
                    places.append(u' '.join([i[0] for i in ne.leaves()]))
        places = list(set(places))
        result = []

        for place in places:
            response=''

            response = db.Geo.find_one({'$or': [{"city_name": place},
                                            {"country_name": place},
                                            {"subdivision_name": place},

                                            ]})
            if response:
                result.append(list(response))
        return result
