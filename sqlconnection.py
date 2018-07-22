import sqlite3 as lite

class SQLConnection(object):

	def __init__(self, db_path="db/expanded_samples.db"):
		self.con = lite.connect(db_path)
		self.cur = self.con.cursor()
		
	def commit(self):
		self.con.commit()
		
	def close(self):
		self.con.close()
		
	def getNumberOfSamplesToExpand(self, datasetId=0, debug=False):
	
		if datasetId == 0:
			self.cur.execute("SELECT COUNT(*) FROM samples s, datasets d WHERE s.dataset = d.rowid AND s.status = 0")
		else:
			self.cur.execute("SELECT COUNT(*) FROM samples s, datasets d WHERE s.dataset = d.rowid AND s.status = 0 AND d.rowid = ?", (datasetId, ))
		
		rows = self.cur.fetchall()

		if debug:
			print(rows)
			
		return rows

	def getSamplesToExpand(self, datasetId=0, debug=False):

		if datasetId == 0:
			self.cur.execute("SELECT s.rowid, s.message, s.status FROM samples s, datasets d WHERE s.dataset = d.rowid AND s.status = 0 ORDER BY RANDOM() LIMIT 10")
		else:
			self.cur.execute("SELECT s.rowid, s.message, s.status FROM samples s, datasets d WHERE s.dataset = d.rowid AND s.status = 0 AND d.rowid = ? ORDER BY RANDOM() LIMIT 10", (datasetId, ))
		
		rows = self.cur.fetchall()

		if debug:
			print(rows)
			
		return rows

	def updateSample(self, sampleId):
	
		self.cur.execute("UPDATE samples SET status = 1 WHERE rowid = ?", (sampleId,))
	
	def insertExpanded(self, sampleId, new_sample):
	
		self.cur.execute("INSERT INTO expanded (orig_sample, message) VALUES (?,?)", (sampleId, new_sample))
		
	def insertDataset(self, datasetName):
	
		self.cur.execute("INSERT INTO datasets (name) VALUES (?)", (datasetName,))
		self.commit()
		
		return self.cur.lastrowid
		
	def insertSample(self, datasetId, label, message):
	
		self.cur.execute("INSERT INTO samples (dataset, status, message, label) VALUES (?, ?, ?, ?)", (datasetId, 0, message, str(label)))		