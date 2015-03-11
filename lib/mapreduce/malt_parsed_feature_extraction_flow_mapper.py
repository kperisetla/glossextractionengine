#!/usr/bin/python
import sys
import re
import cStringIO

# add library to path
sys.path.insert(0, 'glossextractionengine.mod')

from lib.feature_extractor.malt_parsed_pos_context_sequence_feature_extractor import MaltParsedPOSContextSequenceFeatureExtractor

# mapper side - class that acts as proxy for feature extractor for malt parsed sentences
class MaltParsedFeatureExtractionFlowMapper:
    def __init__(self, context_window_size=4, prime_feature_length=4, add_prime_feature = False):
        # get hold of suitable feature extractor
        # k_param: pass 4 tokens as context window length:
        self.feature_extractor = MaltParsedPOSContextSequenceFeatureExtractor(k_param=context_window_size,prime_feature_length=prime_feature_length, add_prime_feature=add_prime_feature)

    def process(self, line):
        try:
            result = self.feature_extractor.extract_features(line)
            if isinstance(result, list):
                for _item in result:
                    feature_dict,category,word = _item

                    # if not category is None and not word is None:
                        # not printing category as it will be always None for Test dataset
                    if not feature_dict is None:
                        print word,"\t",feature_dict,"\t",line
            else:
                feature_dict,category,word = result
                if not feature_dict is None:
                    print word,"\t",feature_dict,"\t",line
        except Exception as ex:
            print >>sys.stderr,ex.message
            pass


if __name__ == '__main__':
    if len(sys.argv)<2:
        print "Too few arguments to instantiate MaltParsedFeatureExtractionFlowMapper"
        exit()

    # use the 2nd parameter as user params since 1st param is the model file name provided by user
    _args = sys.argv[2]
    params = _args.split("#")
    _context_window_size = int(params[0])
    _prime_feature_length = int(params[1])
    _add_prime_feature = bool(params[2])

    _instance = MaltParsedFeatureExtractionFlowMapper(context_window_size=_context_window_size, prime_feature_length=_prime_feature_length, add_prime_feature=_add_prime_feature)

    # a single line is <category> '<instance_name> | <instance>
    for line in sys.stdin:
        line = line.strip()
        _instance.process(line)