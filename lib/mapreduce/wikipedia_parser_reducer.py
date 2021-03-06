#!/usr/bin/python
import sys
import cStringIO

# add library to path
sys.path.insert(0, 'glossextractionengine.mod')

# reducer side - parser class for parsing wikipedia articles dump
class WikipediaParserReducer:
    def __init__(self):
        self.buff = cStringIO.StringIO()
        self.article_title = False
        self.sentence = False
        self._definition_key = None
        self._nondefinition_key = None
        self._definition_score = None
        self._nondefinition_score = None

    # method to print the definitions in a specific format
    def save_definition(self):
        print "%s '%s | %s" % (self._definition_score,self.article_title.strip(),self.sentence)

    # method to print the non definitions in a specific format
    def save_non_definitions(self):
        print "%s '%s | %s" % (self._nondefinition_score,self.article_title.strip(),self.sentence)

if __name__ == '__main__':
    _instance = WikipediaParserReducer()
    # setting the keys for defnitions and non definitions
    _instance._definition_key = "DEF"
    _instance._nondefinition_key = "NONDEF"

    _instance._definition_score = "1"
    _instance._nondefinition_score = "-1"

    # a single line is <TYPE_KEY>\t<article_title>\t<def_or_non_def_based on TYPE_LEY>
    for line in sys.stdin:
        # if valid <TYPE_KEY>\t<article_title>\t<def_or_non_def_based on TYPE_LEY> format
        if "\t" in line:
            _collection = line.split("\t")
            _type_key = _collection[0].strip()
            _instance.article_title = _collection[1].strip()
            _instance.sentence = _collection[2].strip()

            # print >>sys.stderr,"KEY:",_type_key," SENTENCE:",_instance.sentence
            if not _type_key is None:
                if _type_key == _instance._definition_key:
                    _instance.save_definition()
                if _type_key == _instance._nondefinition_key:
                    _instance.save_non_definitions()
