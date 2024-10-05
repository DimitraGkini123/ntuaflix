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
tsv_file_path = '/path/to/truncated_title.crew.tsv'

# Read data from TSV file into a DataFrame
df = pd.read_csv(tsv_file_path, sep='\t')

# Replace \\N with np.nan in the birthYear and deathYear columns
df['directors'] = df['directors'].replace('\\N', np.nan)
df['writers'] = df['writers'].replace('\\N', np.nan)

# Replace NaN values with None
df.replace({np.nan: None}, inplace=True)

# Connect to the database
# ...

# Connect to the database
connection = pymysql.connect(**config)
cursor = connection.cursor()

# Iterate over DataFrame rows and insert into director and writer tables
for index, row in df.iterrows():
    # Remove prefix "nm" from nconst and "tt" from knownForTitles
    tconst = row['tconst'][2:]
    
    # Insert into director table
    directors = [nconst[2:] for nconst in (row['directors'].split(',') if row['directors'] else [])]
    if directors:
        directors_query = """
            INSERT INTO director (name_basicsnconst, title_basicstconst)
            VALUES (%s, %s)
        """
        for nconst in directors:
            nconst_int = int(nconst) if nconst else None
            cursor.execute(directors_query, (nconst_int, tconst))

    # Insert into writer table
    writers = [nconst[2:] for nconst in (row['writers'].split(',') if row['writers'] else [])]
    if writers:
        writers_query = """
            INSERT INTO writer (name_basicsnconst, title_basicstconst)
            VALUES (%s, %s)
        """
        for nconst in writers:
            nconst_int = int(nconst) if nconst else None

            # Check if the name_basicsnconst value exists in the name_basics table
            check_query = "SELECT nconst FROM name_basics WHERE nconst = %s"
            cursor.execute(check_query, (nconst_int,))
            result = cursor.fetchone()

            if result:
                cursor.execute(writers_query, (nconst_int, tconst))

# Commit the changes and close the connection
connection.commit()
connection.close()
