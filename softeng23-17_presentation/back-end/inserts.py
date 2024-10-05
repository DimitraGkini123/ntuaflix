import pandas as pd
import pymysql
import numpy as np

# Replace with your database connection details
config = {
    'host': 'localhost',
    'user': 'root',
    'password': '2255',
    'database': 'ntuaflix'
}

# Replace with the path to your TSV file

tsv_file_path = '/path/to/truncated_name.basics.tsv'



# Read data from TSV file into a DataFrame
df = pd.read_csv(tsv_file_path, sep='\t')

# Replace \\N with np.nan in the birthYear and deathYear columns
df['birthYear'] = df['birthYear'].replace('\\N', np.nan)
df['deathYear'] = df['deathYear'].replace('\\N', np.nan)

# Replace NaN values with None
df.replace({np.nan: None}, inplace=True)

# Connect to the database
connection = pymysql.connect(**config)
cursor = connection.cursor()

# Iterate over DataFrame rows and insert into name_basics and knownForTitles
for index, row in df.iterrows():
    # Remove prefix "nm" from nconst and "tt" from knownForTitles
    nconst = row['nconst'][2:]
    knownForTitles = [tconst[2:] for tconst in row['knownForTitles'].split(',')]

    # Insert into name_basics using parameterized query
    name_basics_query = """
        INSERT INTO name_basics (nconst, primaryName, birthYear, deathYear, primaryProfession)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(name_basics_query, (nconst, row['primaryName'], row['birthYear'], row['deathYear'], row['primaryProfession']))

    # Insert into knownForTitles using parameterized query with tconst as integer
    if knownForTitles:
        knownForTitles_query = """
            INSERT INTO knownForTitles (name_basicsnconst, title_basicstconst)
            VALUES (%s, %s)
        """
        for tconst in knownForTitles:
            tconst_int = int(tconst) if tconst else None
            cursor.execute(knownForTitles_query, (nconst, tconst_int if tconst_int is not None else 0))

# Commit the changes and close the connection
connection.commit()
connection.close()
