import glob, os
import pickle

def compact_meanings():

	meanings = pickle.load( open( "meanings.p", "rb" ) )
	complete_file = meanings
	print(len(complete_file))

	for file in glob.glob("meanings_*.p"):
		print(file)
		meanings = pickle.load( open( file, "rb" ) )
		complete_file.update(meanings)
		print(len(complete_file))
		meanings = complete_file
		pickle.dump( meanings, open( "meanings.p", "wb" ) )
		os.remove(file)
		
compact_meanings()