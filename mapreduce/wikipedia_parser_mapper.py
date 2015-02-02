#!/usr/bin/python
import sys,re
import cStringIO
import xml.etree.ElementTree as xml

# add library to path
sys.path.insert(0, 'glossextractionengine.mod')

from extractor.wikipedia_extractor import WikipediaExtractor

# mapper side - parser class for parsing wikipedia articles dump
class WikipediaParserMapper:
    def __init__(self):
        self.buff = cStringIO.StringIO()
        self.article_title = False
        self.article_raw_text = False
        self._definition_key = None
        self._nondefinition_key = None

    # method to remove tags and replace newlines with spaces
    def normalize(self, raw):
        result = re.sub(r'<.*>',' ',raw)
        result = re.sub(r'\n',' ',result)
        result = re.sub(r'\t',' ',result)
        return result

    # method that processes each line input to mapper
    def process(self):
        _wikipedia_extractor = WikipediaExtractor()
        _def_list = _wikipedia_extractor.get_definitions(self.article_raw_text)
        _non_def_list = _wikipedia_extractor.get_non_definitions(self.article_raw_text)
        self.emit_definitions(self.article_title, _def_list)
        self.emit_non_definitions(self.article_title, _non_def_list)

    # method to emit all definitions with common definition key so that all definitions are accumulated at a single reducer
    def emit_definitions(self, article_title, definition_list):
        print "got definitions:",definition_list
        if not definition_list is None:
            for definition_item in definition_list:
                print self._definition_key,"\t",article_title,"\t",definition_item

    # method to emit all non definitions with common non definition key so that all non definitions are accumulated at a single reducer
    def emit_non_definitions(self, article_title, non_definition_list):
        if not non_definition_list is None:
            for non_definition_item in non_definition_list:
                print self._nondefinition_key,"\t",article_title,"\t",non_definition_item



if __name__ == '__main__':
    _instance = WikipediaParserMapper()
    # setting the keys for defnitions and non definitions
    _instance._definition_key = "DEF"
    _instance._nondefinition_key = "NONDEF"

    # a single line is <article_title>\t<raw_article_text>
    for line in sys.stdin:
        line = line.strip()

        _collection = line.split("\t")
        _instance.article_title = _collection[0]
        _instance.article_raw_text = _collection[1]
        _instance.process()
