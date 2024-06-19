import sqlite3
import pandas as pd

# Connect to the SQLite database
conn = sqlite3.connect('surf_data.db')  # Relative path assuming it's in the same directory as this script

# Query all data
df = pd.read_sql_query("SELECT * FROM SurfData", conn)

# Print the DataFrame
print(df)

# Close the connection
conn.close()
