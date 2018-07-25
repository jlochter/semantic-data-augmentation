import pandas
import json
from sklearn.feature_extraction import stop_words

class Normalization(object):

	def __init__(self, lingo_path="lingo.txt", check_english=True, english_dict_file="words_dictionary.json"):
		self.dict_norm = pandas.read_fwf(lingo_path, header=None, names=["lingo","canonical"], colspecs="infer",index_col=0)
		self.check_english = check_english
		self.english_dict_file = english_dict_file
		self.english_words = []
		
		if check_english:
			try:
				with open(self.english_dict_file,"r") as english_dictionary:
					self.english_words = json.load(english_dictionary)
			except Exception as e:
				print(str(e))

	def transform(self, sample, debug=False):
		normalized = " "
		
		# remove single-and-double quotes
		sample = sample.replace("\"","\'").lower()
		
		if debug:
			print("Sample:    ", sample)
		
		for token in sample.split():
			is_english = False
			if self.check_english:
				if token in self.english_words.keys():
					is_english = True
			
			# if check english = TRUE and word is found in english dict, 
			#    then transform SHOULD NOT apply normalization to token
			if token not in stop_words.ENGLISH_STOP_WORDS and not is_english:
				try:
					token = self.dict_norm.loc[token,'canonical']
				except KeyError:
					token = token
					
			normalized = " ".join([normalized,token]).strip()
			
		if debug:
			print("Normalized:", normalized)
			print("-"*30)
		
		return normalized