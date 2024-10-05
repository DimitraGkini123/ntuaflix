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
tsv_file_path = '/path/to/truncated_name.basics.tsv' # updated file

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

try:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS temp_name_basics (
            nconst INT(10) NOT NULL,
            primaryName VARCHAR(200),
            birthYear INT(4),
            deathYear INT(4),
            primaryProfession VARCHAR(200),
            img_url_asset VARCHAR(255)
        );
    """)

    # Explicitly commit the creation of the temporary table
    connection.commit()
    print("Changes committed successfully.")

    # Iterate over DataFrame rows and insert into name_basics and knownForTitles
    for index, row in df.iterrows():
        # Remove prefix "nm" from nconst
        nconst = row['nconst'][2:]

        # Insert into name_basics using parameterized query
        name_basics_query = """
            INSERT INTO temp_name_basics (nconst, primaryName, birthYear, deathYear, primaryProfession,img_url_asset)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(name_basics_query, (nconst, row['primaryName'], row['birthYear'], row['deathYear'], row['primaryProfession'], row['img_url_asset']))

    # Commit the changes
    connection.commit()
    print("Changes committed successfully.")

except Exception as e:
    print(f"Error: {e}")
    # Rollback changes if there is an error
    connection.rollback()

finally:
    # Close the connection
    connection.close()
