import sqlite3
from crawler import crawl

conn = sqlite3.connect('Tensorview.db')
c = conn.cursor()

#TODO: Delete drop table statements
# TEMP
c.execute("drop table Experiment;")
c.execute("drop table Run;")
c.execute("drop table HyperParameter;")

# Create Experiment table
c.execute('''CREATE TABLE IF NOT EXISTS Experiment (
             eid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
             name varchar(255) NOT NULL);''')

# Create Run table
c.execute('''CREATE TABLE IF NOT EXISTS Run (
             eid INTEGER NOT NULL REFERENCES Experiment (eid),
             rid INTEGER NOT NULL,
             name varchar(255) NOT NULL,
             PRIMARY KEY (eid, rid));''')

# Create HyperParameter table
c.execute('''CREATE TABLE IF NOT EXISTS HyperParameter (
             eid INTEGER NOT NULL REFERENCES Experiment (eid),
             rid INTEGER NOT NULL REFERENCES Run (rid),
             PRIMARY KEY (eid, rid));''')

# Read parameter data from folder
#TODO: RENAME TEST DATA
parameters = crawl('test_data')

# Add experiments and runs into tables
eid = 0
for experiment in parameters:
    eid += 1
    parameters[experiment]['id'] = eid
    c.execute("INSERT OR IGNORE INTO Experiment VALUES(%d, '%s');" % (eid, experiment))

    runs = parameters[experiment]
    rid = 0
    for run in runs:
        if run == 'id':
            continue
        rid += 1
        parameters[experiment][run]['id'] = rid
        c.execute("INSERT OR IGNORE INTO Run VALUES(%d, %d, '%s');" % (eid, rid, run))
        c.execute("INSERT OR IGNORE INTO HyperParameter VALUES(%d, %d)" % (eid, rid))

# Add parameters into table
for experiment in parameters:
    eid = parameters[experiment]['id']
    for run in parameters[experiment]:
        if run == 'id':
            continue
        rid = parameters[experiment][run]['id']
        params = parameters[experiment][run]

        # Hyper parameters
        for hyper in params['hyper']:
            col = [i[1] for i in c.execute("PRAGMA table_info(HyperParameter);")]

            # Type check
            is_str = isinstance(params['hyper'][hyper], str)
            str_format = "'" if is_str else ""

            if hyper not in col:
                c.execute("ALTER TABLE HyperParameter ADD %s %s;" % (hyper, 'varchar(255)' if is_str else 'real'))
                col += [hyper]

            c.execute("UPDATE HyperParameter SET %s = %s%s%s WHERE (eid = %d AND rid = %d);" %
                      (hyper,
                       str_format,
                       params['hyper'][hyper],
                       str_format,
                       eid,
                       rid))

        # Metric parameters
        # Metric tables are stored in "Metric_data_stuff" format
        for metric in params['metric']:
            name = "Metric_" + metric.replace('/', '_')
            c.execute('''CREATE TABLE IF NOT EXISTS %s (
                         eid INTEGER NOT NULL REFERENCES Experiment (eid),
                         rid INTEGER NOT NULL REFERENCES Run (rid),
                         ind INTEGER NOT NULL,
                         val REAL NOT NULL,
                         PRIMARY KEY (eid, rid, ind));''' % name)

            for (i, v) in enumerate(params['metric'][metric]):
                c.execute("INSERT OR IGNORE INTO %s VALUES(%d, %d, %d, %s);" % (name, eid, rid, i, v))


#TODO: delete all the printing stuff
print("Experiment Table")
for row in c.execute("SELECT * FROM Experiment;"):
    print(row)

print("Run Table")
for row in c.execute("SELECT * FROM Run;"):
    print(row)

print("HyperParameter Table")
for row in c.execute("SELECT * FROM HyperParameter;"):
    print(row)

print("metric tables")
for row in c.execute("SELECT * FROM Metric_grad_min;"):
    print(row)

# Commit and close
conn.commit()
conn.close()
