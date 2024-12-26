import duckdb as ddb
import pandas as pd 

df = pd.DataFrame({'cot1': [1, 2, 3, 4, 5], 'cot2': [6, 7, 8, 9, 10]})
print(df)

con = ddb.connect('testduck.db')
# con.execute("CREATE TABLE my_table (id INTEGER, name VARCHAR)")
# con.execute("INSERT INTO my_table VALUES (1, 'Alice'), (2, 'Bob'), (3, 'Charlie')")

# con.execute("EXPORT 'testduck.db'")


df.to_sql('my_test', con, if_exists='append', index=False)
result = con.execute("SELECT * FROM my_test").fetchdf()
print(result)
con.close()

