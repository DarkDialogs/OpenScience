import re
import logging
from os.path import dirname


# Class which contains all the functions responsible for the preprocessing of text.
class Preprocessor:
    # Class Constructor
    def __init__(self, stopword_file_name = dirname(__file__)+"/englishST.txt"):
        '''
        param stopword_file_name: String
            the name of the file to read the stop words from.
        '''
        # Use a list comprehension to read all the stopwords in from the stopwords file one at a time 
        # and slice off the last character (newline character).
        try:
            self.stopwords = {stopword[:-1] for stopword in open(stopword_file_name)}
        except Exception as e:
            logging.warning("Could not find the stopwords file, using stopwords will not work.")


    # Function to apply the various preprocessing steps to the input text in the correct order.
    def preprocess(self, text, fold_case = True, remove_stopwords = False, normalise = False, expand_capitals = False, expand_hypens = False, expand_punctuation = False, ngrams = 1):
        '''
        param text: String
            raw text to be tokenised
        return: List[String]
            a list of tokens with the case folded, stop words removed and stemmed.
        '''
        # Apply all the preprocessing functions in the correct order.
        tokens  = self.tokenise(text)
        if fold_case:
            tokens = self.fold_case(tokens)
        # If remove stopwords option if enabled then remove stopwords from tokens.
        if remove_stopwords:
            tokens = self.remove_stopwords(tokens)
        # If normalise option if enabled then normalise the tokens.
        if normalise:
            tokens = self.normalise(tokens)
        # If expand capitals option if enabled then expand capitals.
        if expand_capitals:
            tokens = self.expand_capitals(tokens, text)
        # If expand hypens option if enabled then expand hypens.
        if expand_hypens:
            tokens = self.expand_hypens(tokens, text)
        # If ngrams option is set to greater than 1 then find all the ngrams of the tokens.
        if ngrams > 1:
            tokens = [" ".join(tokens)]
            logging.debug(tokens)
            tokens = self.find_ngrams(tokens, ngrams)
        # If expand punctuation option if enabled then expand punctuation.
        if expand_punctuation:
            tokens = self.expand_punctuation(tokens, text)
        # If fold case option if enabled then fold case of the tokens.
        return tokens


    # Function to turn raw text into a list of tokens.
    def tokenise(self, text):
        '''
        param text: String
            raw text to be tokenised
        return: List[String]
            a list of tokens.
        '''
        # Compile the regular expression used to split the tokens.
        # Method: Split the text using every non-alphabetical character.
        regex = re.compile("[^a-zA-Z]+")
        # Remove any instances of None from the list 
        # (these are produced by the split method when a non-match occurs)
        return list(filter(None, regex.split(text)))


    # Function to fold the case (lower the case) of a list of tokens.
    def fold_case(self, tokens):
        '''
        param tokens: List[String]
            list of tokens.
        return: List[String]
            a list of tokens with the case folded.
        '''
        # Use a list comprehension to apply the lowercase function to each token.
        tokens = [token.lower() for token in tokens]
        return tokens


    # Function to remove stop words from a list of tokens.
    def remove_stopwords(self, tokens):
        '''
        param tokens: List[String]
            list of tokens.
        return: List[String]
            a list of tokens with the stop words removed.
        '''
        # Note: We use a set to store stopwords as it is much faster to check if a word is in set,
        #  this will speed up the stopword removal process.
        # Use a list comprehension to check if each token is in the set of stopwords.
        tokens = [token for token in tokens if not token in self.stopwords]
        return tokens


    # Function to stem a list of words using the Porter stemmer and return a list of stemmed words.
    def normalise(self, tokens, stemmer = "porter2"):
        '''
        param tokens: List[String]
            list of tokens.
        return: List[String]
            a list of tokens with stemming applied to each token.
        '''
        if stemmer == "porter2":
            from stemming.porter2 import stem
            #Use a list comprehension to apply the stem function from the porter stemmer to each token.
            tokens = [stem(word) for word in tokens]
        elif stemmer == "porter":
            from nltk.stem import PorterStemmer
            ps = PorterStemmer()
            tokens = [ps.stem(word) for word in tokens]
        else:
            logging.warning("Could not find the specified stemmer, using porter 2 instead.")
            from stemming.porter2 import stem
            #Use a list comprehension to apply the stem function from the porter stemmer to each token.
            tokens = [stem(word) for word in tokens]
        return tokens


    # Function to expand a set of tokens to add the punctuation from the original text.
    def expand_punctuation(self, tokens, text):
        # Compile the regular expression used to find all the punctuation.
        regex = re.compile("\!|\"|\#|\$|\%|\&|\'|\(|\)|\*|\+|\,|\-|\.|\/|\:|\;|\<|\=|\>|\?|\@|\[|\\|\]|\^|\_|\`|\{|\||\}|\~")
        # Find all the punctuation in the text and store it in a list.
        punctuation = [i for i in re.findall(regex, text)]
        # Add the punctuation to the list of tokens.
        return tokens + punctuation


    # Function to expand a set of tokens to add the versions of words with words with capitals 
    # duplicated.
    def expand_capitals(self, tokens, text):
        # Find all instances of words with upper-case letters in in the text and add them to a list.
        upper_tokens = [token for token in self.tokenise(text) if any(x.isupper() for x in token)]
        # Add the upper case version of words to the list of tokens.
        return tokens + upper_tokens
        

    # Function to expand a set of tokens to add words separated by hypens with hypens kept.
    def expand_hypens(self, tokens, text):
        # Compile the regular expression used to find all the hypenated words.
        regex = re.compile("\w+(?:-\w+)+")
        # Find all the hypenated words in the text and add them a list.
        hypens = [i for i in re.findall(regex, text)]
        # Add the hypenated words to the tokens.
        return tokens + hypens

    def find_ngrams(self, text, num):
        from nltk import ngrams
        ngram_text = []
        for n in range(1,num+1):
            for sentence in text:
                raw_ngrams = [" ".join(ngram) for ngram in ngrams(sentence.split(), n)]
                ngram_text += raw_ngrams
        return ngram_text
    
    def translate_text(self, raw_text):
        from googletrans import Translator
        translator = Translator()
        """ Function to translate text to English

        Args:
            raw_text (String): the text to be translated

        Returns:
            String: the translated text
        """
        # If the text is not blank then
        if raw_text.rstrip() != "":
            try:
                # Check the language of the raw_text
                lang = translator.detect(raw_text).lang
                # If the language is not English then
                if lang != "en":
                    # Translate the text to English.
                    raw_text = translator.translate(raw_text).text
            # Catch any exceptions.
            except Exception as e:
                logging.warning("Failed to translate.")
        return raw_text
