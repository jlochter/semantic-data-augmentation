import pandas
import json
from sklearn.feature_extraction import stop_words

lingo = pandas.read_fwf("lingo.txt", header=None, names=["lingo","canonical"], colspecs="infer",index_col=0)
eng_dict = json.load(open("words_dictionary.json","r"))

new_lingo = open("new_lingo.txt","w")

for l, c in lingo.itertuples():
	if l in eng_dict.keys():
		continue
	new_lingo.write(str(l) + "\t" + str(c) + "\n")