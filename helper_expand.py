import normalization as normtool
import permutation as permtool
import sqlconnection as conntool

sqlcon = conntool.SQLConnection("db/sentiment.db")

your_api_key = ""

norm = normtool.Normalization()
perm = permtool.Permutation(api_key=your_api_key, max_meanings=3, use_local_meanings=True)

counter_save_local_meanings = 0

while True:

	progress = sqlcon.getNumberOfSamplesToExpand()
	print(progress)

	samplesToExpand = sqlcon.getSamplesToExpand()
	if len(samplesToExpand) == 0:
		break
		
	for sample in samplesToExpand:
		sampleId, message, status = sample

		text = norm.transform(message)
		disambiguation_set = perm.getDisambiguation(text)
		meanings = perm.getMeanings(disambiguation_set)
		new_samples = perm.transform(text, disambiguation_set, meanings, random_sampling_k=200)

		for new_sample in new_samples:
			sqlcon.insertExpanded(sampleId, new_sample)

		sqlcon.updateSample(sampleId)
		sqlcon.commit()
		
	counter_save_local_meanings = counter_save_local_meanings + 1
		
	if counter_save_local_meanings == 10:
		perm.save_local_meanings()
		counter_save_local_meanings = 0
	
perm.save_local_meanings()
