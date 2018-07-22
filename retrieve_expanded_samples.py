import sqlite3 as lite
import csv
import pandas as pd

con = lite.connect("db/semantic_augmentation.db")
cur = con.cursor()

sql = "SELECT rowid as sample_group, message, 1 as orig, label FROM samples WHERE dataset = 1 " + \
      "UNION ALL " + \
      "SELECT orig_sample, message, 0, '' as label FROM expanded " + \
        "WHERE orig_sample IN (SELECT rowid FROM samples WHERE dataset = 1)"

df = pd.read_sql_query(sql, con)
df.sort_values('sample_group')
df.to_csv(path_or_buf='data_augmentated.csv', sep=",", quoting=csv.QUOTE_MINIMAL, doublequote=True, encoding='UTF_8')