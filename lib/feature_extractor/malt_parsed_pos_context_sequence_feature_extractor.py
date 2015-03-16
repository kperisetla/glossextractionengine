#!/usr/bin/python
import sys
# add library to path
sys.path.insert(0, 'glossextractionengine.mod')

from lib.feature_extractor.base_feature_extractor import BaseFeatureExtractor
from lib.feature_extractor.malt_parsed_sentence_feature_extractor import MaltParsedSentenceFeatureExtractor
from lib.feature_extractor.malt_parsed_lexicalized_ngrams_feature_extractor import MaltParsedLexicalizedNgramsFeatureExtractor
import re
from lib.filter.english_token_filter import EnglishTokenFilter

KPARAM = "ALL"
# defines the length of n-gram to be considered in the context as prime feature of the instance
PRIME_FEATURE_LENGTH = 4

# class that extracts contextual features based on Part of speech tags around the word of interest
# NOTE: It assumes you have pos tags and tokens already extracted either through malt parsed sentence feature extractor or by other means
class MaltParsedPOSContextSequenceFeatureExtractor(BaseFeatureExtractor):

    def __init__(self, k_param, prime_feature_length=PRIME_FEATURE_LENGTH, add_prime_feature=False):
        self.k_param = k_param
        self.prime_feature_length = prime_feature_length
        self.add_prime_feature = add_prime_feature
        self.debugFlag = 0 # off by default

        self.english_filter = EnglishTokenFilter()
        self.lex_fe = MaltParsedLexicalizedNgramsFeatureExtractor(n=2)
        pass

    def debug(self,s):
        if self.debugFlag==1:
            print s

    # method that generates sequence model considering all words in the sentence
    # params- result_tuple with category, word, tokens
    def getFullSentenceSequenceModel(self, result_tuple):
        category,word,tokens,sentence,_old_word = result_tuple
        pos_tags = self.word_pos_tuple_collection

        feature_dict = {}
        for i,tpl in enumerate(pos_tags):
            key ="W"+str(i)
            wrd,p_tg = tpl
            val = p_tg
            feature_dict[key] = val
        return feature_dict

    # method that generates sequence model considering only k words from beginning of the line
    # params- result_tuple with category, word, tokens
    # returns a dictionary with features
    def getKSequenceModel(self, result_tuple):
        category,word,tokens,sentence,_old_word = result_tuple
        pos_tags = self.word_pos_tuple_collection
        feature_dict = {}
        for i,tpl in enumerate(pos_tags):

            # read k features- then break
            if i>self.k_param:
                break
            key ="W"+str(i)
            wrd,p_tg = tpl
            val = p_tg
            feature_dict[key] = val
        return feature_dict

    # method that gives start and end index of tokens to be considered for sequence model if NP lies in first half of the sentence
    def getIndicesFirstHalf(self,index,num_of_tokens):
        self.debug("num_of_tokens:"+str(num_of_tokens))
        self.debug("index got in getIndicesFirstHalf:"+str(index))

        self.debug("k_param:"+str(self.k_param))
        if num_of_tokens<self.k_param:
            start_index = 0
            end_index = num_of_tokens - 1
            return (start_index,end_index)

        while( (num_of_tokens)-index)< self.k_param:
            index = index -1
        start_index = index
        end_index = index + self.k_param
        return (start_index,end_index)

    # method that gives start and end index of tokens to be considered for sequence model if NP lies in second half of the sentence
    def getIndicesSecondHalf(self,index,num_of_tokens):
        if num_of_tokens<self.k_param:
            start_index = 0
            end_index = num_of_tokens - 1
            return (start_index,end_index)

        while(index)< self.k_param:
            index = index +1
        start_index = index-self.k_param+1
        end_index = index+1
        return (start_index,end_index)

    # method that gives start and end index of tokens to be considered for sequence model if NP lies at middle of the sentence
    def getIndicesForMiddleWord(self,index,num_of_tokens):
        if num_of_tokens<self.k_param:
            start_index = 0
            end_index = num_of_tokens - 1
            return (start_index,end_index)

        if self.k_param % 2==0:
            start_index = index -(self.k_param/2)
            end_index = index + (self.k_param/2)
        else:
            start_index = index -(self.k_param/2)
            end_index = index + (self.k_param/2)+1
        return (start_index,end_index)

    # method that reads tokens and returns feature_dict
    def getSequenceModelForIndexRange(self,result_tuple,index,start_index,end_index):
        category,word,tokens,sentence,_old_word = result_tuple
        pos_tags = self.word_pos_tuple_collection

        self.debug(pos_tags)

        feature_dict = {}

        # # add feature for tokens from index to start_index
        # token_i = 1
        # if start_index!=index:
        #     for lower in range(index-1,start_index,-1):
        #         key = "W-"+str(token_i)
        #         wrd,p_tg = pos_tags[lower]
        #         val = p_tg
        #         feature_dict[key] = val
        #         token_i = token_i + 1
        #
        # # add feature for token at index
        # key = "W0"
        # wrd,p_tg = pos_tags[index]
        # val = p_tg
        # feature_dict[key] = val
        #
        # # add feature for tokens from index to end index
        # token_i = 1
        # for upper in range(index+1, end_index):
        #     key = "W+"+str(token_i)
        #     wrd,p_tg = pos_tags[upper]
        #     val = p_tg
        #     feature_dict[key] = val
        #     token_i = token_i + 1

        # adding the prime feature if the add_prime_featue flag is set to True
        if self.add_prime_feature:
            self.debug("got features, looking for prime_feature")
            key="prime_feature"
            val=""
            if start_index==index:
                for i in range(index,index+self.prime_feature_length):
                    wrd,p_tg=pos_tags[i]
                    val=val+p_tg+" "
            elif end_index-1==index:
                self.debug("STR:"+str(index-self.prime_feature_length)+" END:"+str(index+1))
                for i in range(index-self.prime_feature_length,index+1):
                    wrd,p_tg=pos_tags[i]
                    val=val+p_tg+" "
            else:
                while(end_index-start_index>=self.prime_feature_length):
                    start_index=start_index+1
                    end_index=end_index-1
                    self.debug("MIDDLE_start_index:"+str(start_index)+" end_index:"+str(end_index))
                for i in range(start_index,end_index):
                    wrd,p_tg=pos_tags[i]
                    val=val+p_tg+" "
            feature_dict[key]=val[:-1]

            # adding prime feature for beginning and ending of the sentence as well
            # for beginning
            beg_pattern = " "
            for k in range(0, self.prime_feature_length):
                wrd,p_tg=pos_tags[k]
                beg_pattern = beg_pattern + p_tg+" "

            feature_dict["beg_prime"] = beg_pattern

            # for ending
            end_pattern = " "
            for k in range(len(pos_tags)-self.prime_feature_length, len(pos_tags)):
                wrd,p_tg=pos_tags[k]
                end_pattern = end_pattern + p_tg+" "
            feature_dict["end_prime"] = end_pattern

        return feature_dict

    # method that takes instance as input and returns feature vector and optional category label
    # params: instance of format- <category> '<instance_name> | <instance>
    # returns: a tuple of (<feature_dict>, <category>, <word>) or a list of such tuples
    def extract_features(self, instance):
        _sentence_feature_extractor = MaltParsedSentenceFeatureExtractor()
        result_tuple = _sentence_feature_extractor.extract_features(instance)

        # copying attributes
        self.token_collection = _sentence_feature_extractor.get_token_collection()
        self.word_pos_tuple_collection = _sentence_feature_extractor.get_word_pos_tuple_collection()

        # malformed instance
        if result_tuple is None:
            return (None,None,None)

        # call _get_seq_model after copying attributes from MaltParsedFeatureExtactor

        # depending on if result_tuple is list or single tuple, take action
        if isinstance(result_tuple,list):
            result_list = []
            for _item in result_tuple:
                result_item = self._get_seq_model(_item)
                result_list.append(result_item)
            return result_list
        else:
            result = self._get_seq_model(result_tuple)
            return result

    def _get_seq_model(self, result_tuple):
        category,word,tokens,sentence,_old_word = result_tuple

        # if word is non english token then return None
        if not self.english_filter.filter(word):
            return (None,None,None)

        # if using test instance
        if category is None and word is None:
            if self.k_param==KPARAM:
                feature_dict = self.getFullSentenceSequenceModel(result_tuple)
            else:
                feature_dict = self.getKSequenceModel(result_tuple)

            return (feature_dict,None, None)


        tokens_set = set(tokens)
        num_of_tokens = len(tokens)

        # if sentence contains the NP
        if word.lower() in sentence.lower():
            self.debug("word in sentence")

            # if the word is not present as complete word in token list 'tokens'
            if tokens.count(word)==0:
                # iterate over tokens
                for token_index,token in enumerate(tokens):
                    # check if word is part of any token
                    if word in token:
                        index=token_index
                        # print(sys.stderr,"containing word found at index :",str(index))

                        break	# found the token containing this word
            else:
                # pick the first index of 'word' in token list 'tokens'
                index = tokens.index(word)	# tokens.index(word)
                # print(sys.stderr,"exact word found at index :",str(index))


            # word lies in first half of the sentence
            if index<num_of_tokens/2:
                self.debug("lies in lower half")
                # print(sys.stderr,"word lies in lower half:going for getIndicesFirstHalf")
                start_index,end_index = self.getIndicesFirstHalf(index,num_of_tokens)
                self.debug("start_index:"+str(start_index)+" end_index:"+str(end_index))

# word lies in second half of the sentence
            if index>num_of_tokens/2:
                start_index,end_index = self.getIndicesSecondHalf(index, num_of_tokens)
                self.debug("lies in second half")
                # print(sys.stderr,"word lies in second half:going for getIndicesSecondHalf")
                self.debug("start_index:"+str(start_index)+" end_index:"+str(end_index))

            # word lies in middle of the sentence
            if index == num_of_tokens/2:
                start_index,end_index = self.getIndicesForMiddleWord(index,num_of_tokens)
                self.debug("lies at the middle")
                # print(sys.stderr,"word lies in middle :going for getIndicesForMiddleWord")
                self.debug("start_index:"+str(start_index)+" end_index:"+str(end_index))

            # get sequence model for tokens in give index range
            feature_dict = self.getSequenceModelForIndexRange(result_tuple,index,start_index, end_index)

            # update feature for multi-word NP
            # feature_dict = self.update_feature_dict(feature_dict,word,_old_word,index)

        else:	# sentence doesn't contains the head NP
            pass


        if not category is None:
            category = category.strip()

        # get the lexicalized features
        # lex_features, lex_category, lex_word = self.lex_fe._get_lexicalize_features(result_tuple)
        # update the feature dict
        # feature_dict.update(lex_features)

        return (feature_dict,category,word)

    # # method to place feature value for W0 as NP if its a multiword NP
    # def update_feature_dict(self, feature_dict, word, old_word`,index):
    #     if word!=old_word:
    #         _tag = "W"+str(index)
    #         feature_dict[_tag] = "NN"
    #     return feature_dict



#
# m = MaltParsedPOSContextSequenceFeatureExtractor(k_param=4)
# m.extract_features("Guests/NNS invited/VBD to/TO the/DT presidential/JJ ball/NN will/MD have/VB to/TO wear/VB tuxedoes/NNS ./.      1")