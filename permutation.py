import json
import requests
import urllib
import pickle
import random

class Permutation(object):

	babelfy_api_url = "https://babelfy.io/v1/disambiguate"
	babelnet_api_url = "https://babelnet.io/v4/getSynset"

	def __init__(self, api_key, lang="EN", use_local_meanings=False, max_meanings=0, check_english=True, english_dict_file="words_dictionary.json"):
		self.lang = lang
		self.key = api_key
		self.use_local_meanings = use_local_meanings
		self.max_meanings = max_meanings
		self.check_english = check_english
		self.english_dict_file = english_dict_file
		self.english_words = []
		
		if use_local_meanings:
			try:
				self.meanings = pickle.load( open( "meanings.p", "rb" ) )
			except:
				self.meanings = {}
				
		if check_english:
			try:
				with open(self.english_dict_file,"r") as english_dictionary:
					self.english_words = json.load(english_dictionary)
			except Exception as e:
				print(str(e))

	def getDisambiguation(self, text, debug=False):
			
		params = {
			"text" : text,
			"lang" : self.lang,
			"key"  : self.key
		}		

		response = requests.get(self.babelfy_api_url + "?" + urllib.parse.urlencode(params), headers={"Accept-encoding": "gzip"})
				
		permut_elements = []
		data = []

		# response from API
		if response.status_code == 200:
			if response.headers['content-type'] == "gzip":
				f = gzip.GzipFile(fileobj=response.content)
				data = json.loads(f)
			else:
				data = json.loads(response.content.decode('utf-8'))
		
		# processing data retrieved
		cfEnd = 0
		
		# sort data considering charFragment.start and length, so it does not consider 'new' when it should consider 'new york'
		data = sorted(data, key=lambda x: (x["charFragment"]["start"], -(x["charFragment"]["end"]-x["charFragment"]["start"]) ))
			
		for result in data:
		
			charFragment = result.get("charFragment")
		
			# verify if next fragment is inside a previous one (case of phrasal nouns)
			if charFragment.get("start") < cfEnd:
				continue

			# define start and end
			cfStart = charFragment.get("start")
			cfEnd = charFragment.get("end")
			
			if debug:
				print(text[cfStart:cfEnd+1])

			# retrieving BabelSynset ID
			synsetId = result.get("babelSynsetID")
			if debug:
				print(synsetId)
			
			permut_elements.append( (cfStart,cfEnd,synsetId) )				
				
		return permut_elements
		
	def getMeanings(self, disambiguation_set, debug=False):
			
		possible_elements = []

		# for each element in disambiguation set, it looks for its meaning in BabelNet
		for el in disambiguation_set:
			
			cfStart, cfEnd, synsetId = el
				
			params = {
				"id" : synsetId,
				"key"  : self.key
			}
			
			# check if there is meaning for that synset already in local data
			if self.use_local_meanings:
				if synsetId in self.meanings.keys():
					replacements = self.meanings[synsetId]
					
					if self.max_meanings > 0:
						if len(replacements) > self.max_meanings:
							replacements = replacements[:self.max_meanings]
							
					possible_elements.append(list(set([x.lower() for x in replacements])))
					continue

			# otherwise, look for meaning in babelnet through API request
			response = requests.get(self.babelnet_api_url + "?" + urllib.parse.urlencode(params), headers={"Accept-encoding": "gzip"})

			replacements = []
			
			# retrieving data
			if response.status_code == 200:
				if response.headers['content-type'] == "gzip":
					f = gzip.GzipFile(fileobj=response.content)
					data = json.loads(f)
				else:
					data = json.loads(response.content.decode('utf-8'))
				
				# processing data retrieved
				if "senses" not in data.keys():
					if debug:
						print(data)
				for result in data["senses"]:
					#if result.get("language") == "EN" and "(" not in result.get("lemma") and "_" not in result.get("lemma") and len(result.get("lemma")) > 1:
					if result.get("language") == "EN" and "(" not in result.get("lemma") and len(result.get("lemma")) > 1:
						meaning = result.get("lemma").replace("_"," ")
						if self.check_english:
							if len(set(meaning.split()).intersection(self.english_words.keys())) == len(meaning.split()):
								replacements.append(meaning)
						else:
							replacements.append(meaning)
				
				if len(replacements) > 0:
					replacements = list(set([x.lower() for x in replacements]))
				
				if self.use_local_meanings:
					self.meanings[synsetId] = replacements
				
				if self.max_meanings > 0:
					if len(replacements) > self.max_meanings:
						replacements = replacements[:self.max_meanings]

			possible_elements.append(replacements)
			
		if debug:
			print(possible_elements)		
		
		return possible_elements
	
	def shrink_elements(self, elements, expansion_limit = 2000):
			
		expansions = float('inf')
		shrinkable = []
		new_elements = []
		meanings = []
		
		for i in elements:
			new_elements.append(i)
			_, _, m = i
			meanings.append(m)
		
		for i in range(len(meanings)):
			if len(meanings[i]) > 1 :
				shrinkable.append(i)
				
		random.shuffle(shrinkable)
		
		while expansion_limit <= expansions:
			
			expansions = 1
			
			for m in meanings:
				m = list(set(m))
				if len(m) > 0:
					expansions *= len(m)
			
			if expansion_limit >= expansions:
				break
			
			# pick a set
			position = shrinkable[-1]
			meanings[position] = random.sample(meanings[position], len(meanings[position])-1)
			
			if len(meanings[position]) <= 1:
				shrinkable.pop()
				
			if len(shrinkable) > 1:
				random.shuffle(shrinkable)
		
		elements = []
		
		for idx, m in enumerate(meanings):
			start, end, _ = new_elements[idx]
			elements.append( (start,end,m) )		
			
		return elements
	
	def transform(self, text, disambiguation_set, meanings, random_sampling_k=0, expansion_limit=2000, debug=False):
	
		if debug:
			print(text)
			print(disambiguation_set)

		elements = []
		last_index = 0
		set_count = 0
		
		start = 0
		end = 0
		
		for start_token, end_token, synsetId in disambiguation_set:
			start = start_token
			end = end_token
			if debug:
				print(start)
				print(end)
				print(synsetId)
			if start > last_index + 1:
				elements.append( (last_index, start - 1, [text[last_index:start - 1].lower().strip()]) )
			
			# add original token to meanings
			meanings[set_count].append(text[start:end+1])
					
			elements.append( (start, end, list(set(meanings[set_count]))) )
			
			last_index = end + 1
			set_count = set_count + 1

		if last_index < len(text):
			elements.append( (last_index, end, [text[last_index:len(text)].lower().strip()]) )
			
		elements = self.shrink_elements(elements, expansion_limit)
			
		if debug:
			print(elements)
			
		new_samples = [""]
		for start, end, meanings in elements:
			aux_samples = []
			for sample in new_samples:
				for meaning in meanings:
					aux_samples.append(" ".join( (sample,meaning) ))
			new_samples = aux_samples
		
		if random_sampling_k > 0 and len(new_samples) > random_sampling_k:
			new_samples = random.sample(new_samples, random_sampling_k)
		
		if debug:
			print(new_samples)
			
		return new_samples
		
	def save_local_meanings(self):
	
		meanings_random_filename = "meanings_" + str(random.randint(1,10000)) + ".p"
	
		pickle.dump( self.meanings, open( meanings_random_filename, "wb" ) )