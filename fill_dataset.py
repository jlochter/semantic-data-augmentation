import pandas as pd
import sqlconnection as connector

sqlcon = connector.SQLConnection("db/semantic_augmentation.db")

data = pd.read_table("SMSSpamCollection.txt", sep="\t", header=None)

datasetId = sqlcon.insertDataset("SMSSpamCollection_preprocessed")

for row in data.itertuples():
    idx, label, message = row
    sqlcon.insertSample(datasetId, label, preprocessing(message))
    
sqlcon.commit()
sqlcon.close()