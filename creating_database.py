import sqlite3 as lite

con = lite.connect("db/semantic_augmentation.db")
cur = con.cursor()

cur.execute("CREATE TABLE datasets(name VARCHAR(40))")
cur.execute("CREATE TABLE samples(dataset INT(4), status INT(1), message TEXT, label VARCHAR(4))")
cur.execute("CREATE TABLE expanded(orig_sample INT(10), message TEXT)")