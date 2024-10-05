from flask import Flask, redirect, render_template, request, jsonify, json, session, url_for, Response
import mysql.connector
from numpy import double
from passlib.hash import bcrypt  # Import the bcrypt hashing library
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import secrets
import csv
from io import StringIO

template_folder_path = r'../front-end/templates'
static_path = r'../front-end/static'

app = Flask(__name__, template_folder=template_folder_path, static_folder=static_path)
app.secret_key = secrets.token_hex(16)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
CORS(app)

# Database configuration
db_config = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "2255",  
    "database": "ntuaflix",
    "charset": "utf8mb4",
    "collation": "utf8mb4_general_ci"
}

try:
    db = mysql.connector.connect(**db_config)
except mysql.connector.Error as err:
    db = None
    print("Database connection failed:", err)


@app.route('/')
def redirect_to_index():
    return redirect('/ntuaflix_api/')

@app.route('/ntuaflix_api/')
def index():
    return render_template('index.html')

@app.route('/ntuaflix_api/homepage.html')
def homepage():
    top_rated_movies = topRated()  
    return render_template('homepage.html', top_rated=top_rated_movies)

@app.route('/ntuaflix_api/signin.html')
def signin():
    return render_template('signin.html')

@app.route('/ntuaflix_api/signup.html')
def signup():
    return render_template('signup.html')

@app.route('/ntuaflix_api/search_title.html')
def search_title():
    return render_template('search_title.html')

@app.route('/ntuaflix_api/search_genre.html')
def search_genre():
    return render_template('search_genre.html')

@app.route('/ntuaflix_api/info/<int:title_ID>')
def info(title_ID):
    return render_template('info.html', title_ID = title_ID)

@app.route('/ntuaflix_api/search_name.html')
def search_name():
    return render_template('search_name.html')

@app.route('/ntuaflix_api/my-list.html')
def my_list():
    return render_template('watching_later.html')

@app.route('/ntuaflix_api/my-likes.html')
def my_likes():
    return render_template('likes.html')

@app.route('/ntuaflix_api/my-history.html')
def my_history():
    return render_template('history.html')

def check_database_connection():
    try:
        # Establish database connection
        db = mysql.connector.connect(**db_config)

        if db.is_connected():
            return {"status": "OK", "dataconnection": db_config}

    except mysql.connector.Error as err:
        return {"status": "failed", "dataconnection": db_config, "error": str(err)}

    finally:
        # Close the database connection when done
        if db.is_connected():
            db.close()

# Health check endpoint
@app.route('/ntuaflix_api/admin/healthcheck', methods=['GET'])
def health_check():
    result = check_database_connection()
    return jsonify(result)  

@app.route('/ntuaflix_api/admin/resetall', methods=['POST'])
def reset_all():
    if request.method == 'POST':
        try:
            # Create a cursor to execute SQL queries
            cursor = db.cursor()

            # Disable foreign key checks
            cursor.execute("SET foreign_key_checks = 0")

            # Execute SQL queries to reset data in each table
            tables_to_reset = [
                "likes",
                "knownForTitles",
                "ListForWatchingLater",
                "title_ratings",
                "title_principals",
                "title_akas",
                "title_episode",
                "writer",
                "director",
                "user_ratings",
                "name_basics",
                "users",
                "title_basics"
            ]

            for table in tables_to_reset:
                query = f"DELETE FROM {table}"
                cursor.execute(query)

            # Enable foreign key checks
            cursor.execute("SET foreign_key_checks = 1")

            # Commit the changes and close the database connection
            db.commit()
            cursor.close()
            db.close()

            return {"status": "OK"}

        except Exception as e:
            print("Status: failed, Reason:", str(e))
            return {"status": "failed", "reason": str(e)}

@app.route('/ntuaflix_api/admin/check')
def admin_check():
    # Retrieve is_admin from the session
    is_admin = session.get('is_admin') 
    print(is_admin)
    # Render the template and pass is_admin to it
    return render_template('admin_check.html', is_admin=is_admin)

@app.route('/ntuaflix_api/signupform', methods=['POST'])
def signupform():
    if request.method == 'POST':
        try:
            # Extract form data
            username = request.form.get('username')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')

            print(username)
            print(password)

            # Check if passwords match
            if password != confirm_password:
                return jsonify({"error": "Passwords do not match"}), 400

            # Hash the password (you should use a secure method for password hashing)

            # Execute the query to insert data into the 'users' table
            cursor = db.cursor()
            query = "INSERT INTO users (Username, password, is_admin) VALUES (%s, %s, 0)"
            cursor.execute(query, (username, password))
            db.commit()

            return redirect(url_for('signup_success'))

        except Exception as e:
            # Handle errors
            print(str(e))
            return jsonify({"error": "Internal server error"}), 500

    return jsonify({"error": "Invalid request"}), 400

@app.route('/ntuaflix_api/signup_success')
def signup_success():
    return render_template('signin.html')

@app.route('/ntuaflix_api/login', methods=['POST'])
def login():
    if request.method == 'POST':
        try:
            # Extract username and password from form data
            username = request.form.get('username')
            password = request.form.get('password')

            if username is None or password is None:
                return jsonify({"error": "Bad request"}), 400
            else:
                cursor = db.cursor()
                # Execute a query to check if the username and password exist in the same row
                query = "SELECT * FROM users WHERE Username = %s AND password = %s"
                cursor.execute(query, (username, password))

                # Fetch the result
                result = cursor.fetchone()
                user_id = result[0]
                print(result)

                if result:
                    user_id, username, is_admin = result[0], result[1], result[3]
                    # Store user ID in the session
                    session['user_id'] = user_id
                    session['is_admin'] = is_admin
                    print("Session after login:", session)
                    
                    return jsonify({"user_id": user_id, "username": username, "is_admin": is_admin}), 200
                else:
                    return jsonify({"error": "Not authorized"}), 401

        except Exception as e:
            # Log the exception for debugging
            print(str(e))
            # Internal server error
            return jsonify({"error": "Internal server error"}), 500
    else:
        return jsonify({"error": "Not Available"}), 404

@app.route('/ntuaflix_api/logout', methods=['POST'])
def logout():
    if request.method == 'POST':
        try:
            print("Session before logout:", session)
            user_id = session.get('user_id')

            if user_id is not None:
                session.pop('user_id')
                session.pop('is_admin')

                print(f"User {user_id} logged out successfully")
                print("Session after logout:", session)
                
                return jsonify({"message": f"User {user_id} logged out successfully"}), 200
            else:
                print("User not logged in")
                return jsonify({"error": "Not logged in"}), 401
        
        except Exception as e:
            print(str(e))
            return jsonify({"error": "Internal server error"}), 500
    else:
        return jsonify({"error": "Not Available"}), 404
    
@app.route('/ntuaflix_api/get_user_id', methods = ['GET'])
def get_user_id():
    user_id = session.get('user_id')

    if user_id:
        return jsonify(user_id), 200
    else:
        return jsonify({"error": "User not authenticated"}), 401
    
def fetch_title_akas(cursor, title_id):
    # Fetch title_akas for a given title
    query_akas = "SELECT title, region FROM title_akas WHERE titleID = %s"
    cursor.execute(query_akas, (title_id,))
    title_akas = cursor.fetchall()
    if title_akas:
        return [{'titleAkas': akas[0], 'regionAbbrev': akas[1]} for akas in title_akas]
    else: 
        return None

def fetch_title_principals(cursor, title_id):
    # Fetch title_principals for a given title
    query_principals = "SELECT tp.name_basicsnconst, nb.Primaryname, tp.category FROM title_principals tp INNER JOIN name_basics nb ON tp.name_basicsnconst = nb.nconst WHERE tp.tconst = %s"
    cursor.execute(query_principals, (title_id,))
    title_principals = cursor.fetchall()
    if title_principals:
        return [{'nameID': str(principal[0]), 'name': principal[1], 'category': principal[2]} for principal in title_principals]
    else:
        return None

def fetch_title_rating(cursor, title_id):
    # Fetch title_rating for a given title
    query_rating = "SELECT averageRating, numVotes FROM title_ratings WHERE tconst = %s"
    cursor.execute(query_rating, (title_id,))
    title_rating = cursor.fetchone()
    return {
    'avRating': str(round(title_rating[0], 2)) if title_rating else None,
    'numVotes': str(title_rating[1]) if title_rating else None
}

@app.route('/ntuaflix_api/title/<int:titleID>', methods=['GET'])
def title(titleID):
    format_arg = request.args.get('format')

    if request.method == 'GET':
        cursor = db.cursor()

        query_basics = "SELECT tconst, titletype, originalTitle, img_url_asset, startYear, endYear, genres FROM title_basics WHERE tconst = %s"
        cursor.execute(query_basics, (titleID,))

        title_data = cursor.fetchone()

        if title_data:
            try:
                column_names = ["titleID", "type", "originalTitle", "titlePoster", "startYear", "endYear", "genres"]
                title = dict(zip(column_names, title_data))
                title['genres'] = title['genres'].split(',') if title['genres'] else []
                title['startYear'] = str(title['startYear'])
                title['titleID'] = str(title['titleID'])

                # Fetch title_akas, title_principals, and title_rating for each title
                title['principals'] = fetch_title_principals(cursor, title_data[0])
                title['rating'] = fetch_title_rating(cursor, title_data[0])

                if format_arg == 'csv':
                    csv_data = convert_to_csv_titleObject(title)
                    return Response(csv_data, mimetype='text/csv') #DOESN'T WORK
                else:
                    return jsonify(title), 200

            except Exception as e:
                print("Error in query_akas execution:", str(e))
                return jsonify({"error": "Internal server error"}), 500

        else:
            return jsonify({"error": "Title not found"}), 204

    else:
        return jsonify({"error": "Not Available"}), 404
    
@app.route('/ntuaflix_api/searchTitle', methods=['GET'])
def searchTitle():
    if request.method == 'GET':
        cursor = db.cursor()

        #data = request.get_json() take the data from the body
        titlePart = request.args.get('titlePart')
        output_format = request.args.get('format', 'json')

        if titlePart:
            query_basics = "SELECT tconst, titletype, originalTitle, img_url_asset, startYear, endYear, genres FROM title_basics WHERE originalTitle LIKE %s"
            cursor.execute(query_basics, (f"%{titlePart}%",))
            titles = cursor.fetchall()

            title_list = []

            for title_info in titles:
                title_dict = {
                    'titleID': str(title_info[0]),
                    'type': title_info[1],
                    'originalTitle': title_info[2],
                    'titlePoster': title_info[3],
                    'startYear': str(title_info[4]),
                    'endYear': str(title_info[5]),
                    'genres': title_info[6].split(',') if title_info[6] else []
                }

                # Fetch title_akas, title_principals, and title_rating for each title
                title_dict['titleAkas'] = fetch_title_akas(cursor, title_info[0])
                title_dict['principals'] = fetch_title_principals(cursor, title_info[0])
                title_dict['rating'] = fetch_title_rating(cursor, title_info[0])
                
                title_list.append(title_dict)

            if output_format == 'csv':
                csv_data = convert_to_csv_titleObject(title_list)
                return Response(csv_data, mimetype='text/csv')

            elif output_format == 'json':
                if title_list:
                    return jsonify(title_list), 200
                else:
                    return jsonify({"error": "Movies not found"}), 204
            else:
                return jsonify({"error": "Invalid format specified"}), 400

    return jsonify({"error": "Not Available"}), 404

@app.route('/ntuaflix_api/bygenre', methods=['GET'])
def bygenre():
    if request.method == 'GET':
        cursor = db.cursor()

        qgenre = request.args.get('qgenre')
        minrating = float(request.args.get('minrating'))
        yrFrom = request.args.get('yrFrom')
        yrTo = request.args.get('yrTo')
        output_format = request.args.get('format', 'json')

        query = "SELECT t.tconst, t.titletype, t.originalTitle, t.img_url_asset, t.startYear, t.endYear, t.genres FROM title_basics t INNER JOIN title_ratings r ON t.tconst = r.tconst WHERE t.genres LIKE %s AND r.averageRating >= %s "
        parameters = [f"%{qgenre}%",minrating]

        if yrFrom and yrTo:
            query += "AND t.startYear >= %s AND t.startYear <= %s"
            parameters.append(int(yrFrom))
            parameters.append(int(yrTo))

        query += " GROUP BY t.tconst, t.titletype, t.originalTitle, t.img_url_asset, t.startYear, t.endYear, t.genres"

        cursor.execute(query,parameters)
        titles = cursor.fetchall()

        title_list = []

        for title_info in titles:
                title_dict = {
                    'titleID': str(title_info[0]),
                    'type': title_info[1],
                    'originalTitle': title_info[2],
                    'titlePoster': title_info[3],
                    'startYear': str(title_info[4]),
                    'endYear': str(title_info[5]),
                    'genres': title_info[6].split(',') if title_info[6] else []
                }

                # Fetch title_akas for each title
                title_dict['titleAkas'] = fetch_title_akas(cursor, title_info[0])
                title_dict['principals'] = fetch_title_principals(cursor, title_info[0])
                title_dict['rating'] = fetch_title_rating(cursor, title_info[0])

                title_list.append(title_dict)
        
        if output_format == 'csv':
            csv_data = convert_to_csv_titleObject(title_list)
            return Response(csv_data, mimetype='text/csv')
        elif title_list:
            return jsonify(title_list), 200
        else:
            return jsonify({"error": "Movies not found"}), 204

    # Return an empty list if no titles are found or if titlePart is not provided
    else:
        return jsonify({"error": "Not Available"}), 404
    
@app.route('/ntuaflix_api/name/<int:nameID>', methods=['GET'])
def name(nameID):
    if request.method == 'GET':
        cursor = db.cursor()

        query_basics = "SELECT nconst, primaryName, img_url_asset, birthYear, deathYear, primaryProfession FROM name_basics WHERE nconst = %s"
        cursor.execute(query_basics,(nameID,))

        name_data = cursor.fetchone()

        if name_data:
            try:
                column_names = ["nameID", "name", "namePoster", "birthYr", "deathYr", "profession"]
                name = dict(zip(column_names, name_data))
                
                query_principals = "SELECT tp.tconst, tp.category FROM title_principals tp INNER JOIN name_basics nb ON tp.name_basicsnconst = nb.nconst WHERE tp.name_basicsnconst = %s"
                cursor.execute(query_principals, (nameID,))
                name_principals = cursor.fetchall()

                if name_principals:
                    name['nameTitles'] = [{"titleID": str(np[0]), "category": np[1]} for np in name_principals]

                return jsonify(name), 200
            except Exception as e:
                print("Error in query_akas execution:", str(e))
                return jsonify({"error": "Internal server error"}), 500

        else:
            return jsonify({"error": "Title not found"}), 204
    
    else:
        return jsonify({"error": "Not Available"}), 404
    
@app.route('/ntuaflix_api/searchname', methods=['GET'])
def searchnamename():
    if request.method == 'GET':
        cursor = db.cursor()

        namePart = request.args.get('namePart')
        output_format = request.args.get('format', 'json')

        query_basics = "SELECT nconst, primaryName, img_url_asset, birthYear, deathYear, primaryProfession FROM name_basics WHERE primaryName LIKE %s"
        cursor.execute(query_basics,(f"%{namePart}%",))

        names = cursor.fetchall()
        name_list = []

        if names:
            for name_data in names:
                column_names = ["nameID", "name", "namePoster", "birthYr", "deathYr", "profession"]
                name = dict(zip(column_names, name_data))
                cursor.fetchall()
                
                query_principals = "SELECT tp.tconst, tp.category FROM title_principals tp INNER JOIN name_basics nb ON tp.name_basicsnconst = nb.nconst WHERE tp.name_basicsnconst = %s"
                cursor.execute(query_principals, (name_data[0],))
                name_principals = cursor.fetchall()
                # Fetch results of query_principals before proceeding
                cursor.fetchall()

                if name_principals:
                    name['nameTitles'] = [{"titleID": str(np[0]), "category": np[1]} for np in name_principals]
                name_list.append(name)
            
            if output_format == 'csv':
                csv_data = convert_to_csv_nameObject(name_list)
                return Response(csv_data, mimetype='text/csv')

            elif output_format == 'json':
                if name_list:
                    return jsonify(name_list), 200
                else:
                    return jsonify({"error": "Movies not found"}), 204
            else:
                return jsonify({"error": "Invalid format specified"}), 400
        
        else:
            return jsonify({"error": "No name found"}), 204
    else:
        return jsonify({"error": "Not Available"}), 404
    
    return jsonify({"error" : "Internal server error"}), 500

@app.route('/ntuaflix_api/topRated', methods=['GET'])
def topRated():
    if request.method == 'GET':
        cursor = db.cursor()
        query_top10 = "SELECT tp.img_url_asset, tr.averageRating, tp.tconst, tp.originalTitle FROM title_basics tp INNER JOIN title_ratings tr ON tp.tconst = tr.tconst WHERE tp.img_url_asset IS NOT NULL ORDER BY tr.averageRating DESC LIMIT 10"
        cursor.execute(query_top10)
        top_rated = cursor.fetchall()

        top_rated_with_width = []

        for result in top_rated:
            img_url = result[0]
            width_variable = 'w200'  # Replace 'w500' with your desired width value
            poster_url = img_url.replace('{width_variable}', width_variable) if img_url else '/static/images/default_image_for_titles.jpeg'
            top_rated_with_width.append({'poster_url': poster_url, 'averageRating': result[1], 'ID': result[2], 'originalTitle': result[3]})

        if top_rated_with_width:
            return jsonify(top_rated_with_width), 200
        else:
            return jsonify({"error": "No movies found"}), 204
    else:
        return jsonify({"error": "Method Not Allowed"}), 405

@app.route('/ntuaflix_api/add_to_list/<int:titleID>', methods=['POST'])
def add_to_list(titleID):
    if request.method == 'POST':
        userID = session.get('user_id')

        if not userID:
            # If user ID is not in the session, handle it accordingly
            return jsonify({"error": "Not authenticated"}), 401

        cursor = db.cursor()
        query_check = "SELECT * FROM ListForWatchingLater WHERE usersid = %s and title_basicstconst  = %s"
        cursor.execute(query_check, (userID, titleID))
        movie = cursor.fetchone()
        
        if movie:
           return jsonify({"message": "Movie already in list"}), 200
        
        else:
            query_add = "INSERT INTO ListForWatchingLater(usersid, title_basicstconst ) VALUES(%s, %s)"
            cursor.execute(query_add, (userID, titleID))
            db.commit()

            if cursor.rowcount > 0 :
                return jsonify({"message": "Movie added succesfully"}), 200
            else:
                return jsonify({"error": "Something went wrong"}), 204
    else:
        return jsonify({"error": "Not Available"}), 404
    
    return jsonify({"error" : "Internal server error"}), 500

@app.route('/ntuaflix_api/remove_from_list/<int:titleID>', methods=['POST'])
def remove_from_list(titleID):
    if request.method == 'POST':
        userID = session.get('user_id')

        if not userID:
            # If user ID is not in the session, handle it accordingly
            return jsonify({"error": "User not authenticated"}), 401

        cursor = db.cursor()
        query_check = "SELECT * FROM ListForWatchingLater WHERE usersid = %s and title_basicstconst = %s"
        cursor.execute(query_check, (userID, titleID))
        movie = cursor.fetchone()
        
        if movie:
            query_remove = "DELETE FROM ListForWatchingLater WHERE usersid = %s and title_basicstconst = %s"
            cursor.execute(query_remove, (userID, titleID))
            db.commit()

            if cursor.rowcount > 0 :
                return jsonify({"message": "Movie removed succesfully"}), 200
            else:
                return jsonify({"error": "Something went wrong"}), 204
        
        else:
            return jsonify({"error" : "Not in list"}), 200
    return jsonify({"error" : "Internal server error"}), 500

@app.route('/ntuaflix_api/list_for_watching_later', methods=['GET'])
def list_for_watching_later():
    if request.method == 'GET':
        userID = session.get('user_id')
        output_format = request.args.get('format', 'json')

        if not userID:
            # If user ID is not in the session, handle it accordingly
            return jsonify({"error": "User not authenticated"}), 401

        cursor = db.cursor()
        query1 = "SELECT * FROM ListForWatchingLater WHERE usersid = %s"

        with db.cursor() as cursor:
            cursor.execute(query1, (userID,))
            movies = cursor.fetchall()

        movie_list = []

        if movies:
            try:
                for movie in movies:
                    query2 = "SELECT t.tconst, t.titletype, t.originalTitle, t.img_url_asset, t.startYear, t.endYear, t.genres FROM title_basics t INNER JOIN ListForWatchingLater l ON t.tconst = l.title_basicstconst WHERE t.tconst = %s"
                    with db.cursor() as cursor:
                        cursor.execute(query2,(movie[1],))
                        movie_info = cursor.fetchone()
                        movie_dict = {
                            'titleID': str(movie_info[0]),
                            'type': movie_info[1],
                            'originalTitle': movie_info[2],
                            'titlePoster': movie_info[3],
                            'startYear': str(movie_info[4]),
                            'endYear': str(movie_info[5]),
                            'genres': movie_info[6].split(',') if movie_info[6] else []
                        }
                        # Fetch title_akas, title_principals, and title_rating for each title
                        movie_dict['titleAkas'] = fetch_title_akas(cursor, movie_info[0])
                        movie_dict['principals'] = fetch_title_principals(cursor, movie_info[0])
                        movie_dict['rating'] = fetch_title_rating(cursor, movie_info[0])

                        movie_list.append(movie_dict)

                if output_format == 'csv':
                    csv_data = convert_to_csv_titleObject(movie_list)
                    return Response(csv_data, mimetype='text/csv')

                elif output_format == 'json':
                    if movies:
                        return jsonify(movie_list), 200
                    else:
                        return jsonify({"error": "Movies not found"}), 204
                else:
                    return jsonify({"error": "Invalid format specified"}), 400
                
            except Exception as e:
                print(f"An exception occurred: {e}")
                return jsonify({"error": "Internal server error"}), 500
        else:
            return jsonify({'list': []}), 200
    else:
        return jsonify({"error": "Method Not Allowed"}), 405

@app.route('/ntuaflix_api/add_to_likes/<int:titleID>', methods=['POST'])
def add_to_likes(titleID):
    if request.method == 'POST':
        userID = session.get('user_id')

        if not userID:
            # If user ID is not in the session, handle it accordingly
            return jsonify({"error": "User not authenticated"}), 401

        cursor = db.cursor()
        query_check = "SELECT * FROM likes WHERE usersid = %s and title_basicstconst  = %s"
        cursor.execute(query_check, (userID, titleID))
        movie = cursor.fetchone()
        
        if movie:
           return jsonify({"message": "Movie already liked"}), 200
        
        else:
            query_add = "INSERT INTO Likes(usersid, title_basicstconst) VALUES(%s, %s)"
            cursor.execute(query_add, (userID, titleID))
            db.commit()

            if cursor.rowcount > 0 :
                return jsonify({"message": "Movie added succesfully"}), 200
            else:
                return jsonify({"error": "Something went wrong"}), 204
    return jsonify({"error" : "Internal server error"}), 500

@app.route('/ntuaflix_api/remove_from_likes/<int:titleID>', methods=['POST'])
def remove_from_likes(titleID):
    if request.method == 'POST':
        userID = session.get('user_id')

        if not userID:
            # If user ID is not in the session, handle it accordingly
            return jsonify({"error": "User not authenticated"}), 401

        cursor = db.cursor()
        query_rem = "DELETE FROM Likes where title_basicstconst = %s"
        cursor.execute(query_rem, (titleID,))
        db.commit()

        if cursor.rowcount > 0 :
            return jsonify({"message": "Movie unliked succesfully"}), 200
        else:
            return jsonify({"error": "Movie already unliked"}), titleID
        
    return jsonify({"error" : "Internal server error"}), 500

@app.route('/ntuaflix_api/check_watchlist/<int:titleID>', methods=['GET'])
def check_watchlist(titleID):
        userID = session.get('user_id')

        if not userID:
            # If user ID is not in the session, handle it accordingly
            return jsonify({"error": "User not authenticated"}), 401

        # Create a cursor to execute SQL queries
        cursor = db.cursor()

        # Check if the movie with titleID is in the watchlist for the current user
        query = "SELECT * FROM ListForWatchingLater WHERE usersid = %s AND title_basicstconst = %s"
        cursor.execute(query, (userID, titleID))

        # Fetch the result
        result = cursor.fetchone()

        # Check if fetchone() returned a result
        in_watchlist_count = result[1] if result and result[1] is not None else 0
        #print(in_watchlist_count)
        
        # Return a JSON response indicating whether the movie is in the watchlist or not
        return jsonify({'inWatchlist': in_watchlist_count}), 200, {'Content-Type': 'application/json'}

@app.route('/ntuaflix_api/check_likelist/<int:titleID>', methods=['GET'])
def check_likelist(titleID):
        userID = session.get('user_id')

        if not userID:
            # If user ID is not in the session, handle it accordingly
            return jsonify({"error": "User not authenticated"}), 401

        # Create a cursor to execute SQL queries
        cursor = db.cursor()

        # Check if the movie with titleID is in the watchlist for the current user
        query = "SELECT * FROM Likes WHERE usersid = %s AND title_basicstconst = %s"
        cursor.execute(query, (userID, titleID))

        # Fetch the result
        result = cursor.fetchone()

        # Check if fetchone() returned a result
        in_likelist_count = result[0] if result and result[0] is not None else 0
        #print(in_watchlist_count)

        # Return a JSON response indicating whether the movie is in the watchlist or not
        return jsonify({'inLikelist': in_likelist_count}), 200, {'Content-Type': 'application/json'}

@app.route('/ntuaflix_api/likes', methods=['GET'])
def likes():
    if request.method == 'GET':
        userID = session.get('user_id')
        output_format = request.args.get('format', 'json')
        if not userID:
            # If user ID is not in the session, handle it accordingly
            return jsonify({"error": "User not authenticated"}), 401

        cursor = db.cursor()
        query1 = "SELECT * FROM Likes WHERE usersid = %s"
        cursor.execute(query1, (userID,))
        movies = cursor.fetchall()

        movie_list = []

        if movies:
            for movie in movies:
                query2 = "SELECT t.tconst, t.titletype, t.originalTitle, t.img_url_asset, t.startYear, t.endYear, t.genres FROM title_basics t INNER JOIN Likes l ON t.tconst = l.title_basicstconst WHERE t.tconst = %s"
                cursor.execute(query2,(movie[1],))
                movie_info = cursor.fetchone()
                movie_dict = {
                    'titleID': str(movie_info[0]),
                    'type': movie_info[1],
                    'originalTitle': movie_info[2],
                    'titlePoster': movie_info[3],
                    'startYear': str(movie_info[4]),
                    'endYear': str(movie_info[5]),
                    'genres': movie_info[6].split(',') if movie_info[6] else []
                }

                # Fetch title_akas, title_principals, and title_rating for each title
                movie_dict['titleAkas'] = fetch_title_akas(cursor, movie_info[0])
                movie_dict['principals'] = fetch_title_principals(cursor, movie_info[0])
                movie_dict['rating'] = fetch_title_rating(cursor, movie_info[0])

                movie_list.append(movie_dict)

            if output_format == 'csv':
                csv_data = convert_to_csv_titleObject(movie_list)
                return Response(csv_data, mimetype='text/csv')

            elif output_format == 'json':
                if movie_list:
                    return jsonify(movie_list), 200
                else:
                    return jsonify({"error": "Movies not found"}), 204
            else:
                return jsonify({"error": "Invalid format specified"}), 400
    else:
        return jsonify({"error": "Method Not Allowed"}), 405
        
    return jsonify({"error" : "Internal server error"}), 500

@app.route('/ntuaflix_api/check_myratingslist', methods=['GET'])
def check_myratingslist():
    if request.method == 'GET':
        userID = session.get('user_id')
        output_format = request.args.get('format', 'json')
        if not userID:
            # If user ID is not in the session, handle it accordingly
            return jsonify({"error": "User not authenticated"}), 401

        cursor = db.cursor()
        query1 = "SELECT * FROM user_ratings WHERE usersid = %s"
        cursor.execute(query1, (userID,))
        movies = cursor.fetchall()

        movie_list = []

        if movies:
            for movie in movies:
                query2 = "SELECT t.tconst, t.titletype, t.originalTitle, t.img_url_asset, t.startYear, t.endYear, t.genres FROM title_basics t INNER JOIN user_ratings ur ON t.tconst = ur.title_basicstconst WHERE t.tconst = %s"
                cursor.execute(query2,(movie[1],))
                movie_info = cursor.fetchone()
                movie_dict = {
                    'titleID': str(movie_info[0]),
                    'type': movie_info[1],
                    'originalTitle': movie_info[2],
                    'titlePoster': movie_info[3],
                    'startYear': str(movie_info[4]),
                    'endYear': str(movie_info[5]),
                    'genres': movie_info[6].split(',') if movie_info[6] else []
                }

                # Fetch title_akas, title_principals, and title_rating for each title
                movie_dict['titleAkas'] = fetch_title_akas(cursor, movie_info[0])
                movie_dict['principals'] = fetch_title_principals(cursor, movie_info[0])
                movie_dict['rating'] = fetch_title_rating(cursor, movie_info[0])

                movie_list.append(movie_dict)

            if output_format == 'csv':
                csv_data = convert_to_csv_titleObject(movie_list)
                return Response(csv_data, mimetype='text/csv')

            elif output_format == 'json':
                if movie_list:
                    return jsonify(movie_list), 200
                else:
                    return jsonify({"error": "Movies not found"}), 204
            else:
                return jsonify({"error": "Invalid format specified"}), 400
    else:
        return jsonify({"error": "Method Not Allowed"}), 405
        
    return jsonify({"error" : "Internal server error"}), 500


@app.route('/ntuaflix_api/check_rating/<int:titleID>', methods=['GET'])
def check_rating(titleID):
    userID = session.get('user_id')

    if not userID:
        return jsonify({"error": "User not authenticated"}), 401

    cursor = db.cursor()
    query = "SELECT * FROM user_ratings WHERE usersid = %s AND title_basicstconst = %s"
    cursor.execute(query, (userID, titleID))
    result = cursor.fetchone()

    if result:
        # User has already rated the movie
        return jsonify({"rated": True}), 200
    # User has not rated the movie yet
    return jsonify({"rated": False}), 200
    
@app.route('/ntuaflix_api/rating/<int:titleID>', methods = ['POST'])
def rating(titleID):
    if request.method == 'POST':
        try:
            data = request.json
            rating = int(data['rating'])
            #rating = int(request.form.get('rating'))
            comment = str(data['comment'])
            #comment = str(request.form.get('comment','')) # If the field is not filled in by the user, it will return an empty string ('')
            userID = session.get('user_id')

            if not userID:
            # If user ID is not in the session, handle it accordingly
                return jsonify({"error": "User not authenticated"}), 401
            
            cursor = db.cursor()
            query_prev_rating = "SELECT rating FROM user_ratings WHERE usersid = %s AND title_basicstconst = %s"
            cursor.execute(query_prev_rating, (userID, titleID))
            prev_rating_row = cursor.fetchone()
            cursor.close()
            if prev_rating_row:
                return jsonify({"message": "Movie already rated"}), 200
            if rating is None:
                return jsonify({"message": "Bad request"}), 400
            else:
                cursor = db.cursor()
                query_user_rating = "INSERT INTO user_ratings(usersid, title_basicstconst, rating, comment) VALUES(%s,%s,%s,%s)"
                cursor.execute(query_user_rating,(userID,titleID,rating,comment))
                db.commit()

                if cursor.rowcount > 0:
                    query_movie_ratings = "UPDATE title_ratings SET numVotes = numVotes + 1, averageRating = (averageRating * numVotes + %s)/(numVotes + 1) WHERE tconst = %s"
                    cursor.execute(query_movie_ratings,(rating,titleID))
                    db.commit()

                    if cursor.rowcount > 0:
                        return jsonify({"message": "Rating added succesfully"}), 200
                    else:
                        return jsonify({"message": "No rating added"}), 204
                else:
                    return jsonify({"message": "No rating added"}), 204
        except Exception as e:
            print(str(e))
            # Internal server error
            return jsonify({"error": "Internal server error"}), 500
    else:
        return jsonify({"error": "Not Available"}), 404

@app.route('/ntuaflix_api/replace_rating/<int:titleID>', methods=['PUT'])
def replace_rating(titleID):
    if request.method == 'PUT':
        try:
            data = request.json
            new_rating = int(data['rating'])
            comment = str(data['comment'])
            userID = session.get('user_id')

            if not userID:
                return jsonify({"error": "User not authenticated"}), 401

            cursor = db.cursor()
            # Get the previous rating and comment
            query_prev_rating = "SELECT rating FROM user_ratings WHERE usersid = %s AND title_basicstconst = %s"
            cursor.execute(query_prev_rating, (userID, titleID))
            prev_rating_row = cursor.fetchone()

            if not prev_rating_row:
                return jsonify({"error": "No previous rating found"}), 404

            prev_rating = prev_rating_row[0]

            # Update the user's rating and comment
            query_update_rating = "UPDATE user_ratings SET rating = %s, comment = %s WHERE usersid = %s AND title_basicstconst = %s"
            cursor.execute(query_update_rating, (new_rating, comment, userID, titleID))

            # Update the movie's average rating
            query_update_avg_rating = "UPDATE title_ratings SET averageRating = averageRating + (%s - %s) / numVotes WHERE tconst = %s"
            cursor.execute(query_update_avg_rating, (new_rating, prev_rating, titleID))

            db.commit()

            if cursor.rowcount > 0:
                return jsonify({"message": "Rating replaced successfully"}), 200
            else:
                return jsonify({"message": "No rating replaced"}), 204
        except Exception as e:
            print(str(e))
            return jsonify({"error": "Internal server error"}), 500
    else:
        return jsonify({"error": "Not Available"}), 404


@app.route('/ntuaflix_api/movie_info/<int:titleID>', methods=['GET'])
def movie_info(titleID):
    if request.method == 'GET':
        cursor = db.cursor()

        query_basics = "SELECT tconst, titletype, originalTitle, img_url_asset, startYear, endYear, genres FROM title_basics WHERE tconst = %s"
        cursor.execute(query_basics,(titleID,))

        movie_data = cursor.fetchone()

        if movie_data:
            try:
                column_names = ["titleID", "type", "originalTitle", "titlePoster", "startYear", "endYear", "genres"]
                movie = dict(zip(column_names, movie_data))
                movie['genres'] = movie['genres'].split(',') if movie['genres'] else [] 
                movie['startYear'] = str(movie['startYear'])
                movie['titleID'] = str(movie['titleID'])

                # Fetch title_akas, title_principals, and title_rating for each title
                query_akas = "SELECT title, region FROM title_akas WHERE titleID = %s"
                cursor.execute(query_akas, (titleID,))
                title_akas = cursor.fetchall()

                if title_akas:
                     movie['titleAkas'] = [{'titleAkas': akas[0], 'regionAbbrev': akas[1]} for akas in title_akas]
                
                # We also select the principals images when we display the movie information
                query_principals = "SELECT tp.name_basicsnconst, nb.Primaryname, tp.category, nb.img_url_asset FROM title_principals tp INNER JOIN name_basics nb ON tp.name_basicsnconst = nb.nconst WHERE tp.tconst = %s"
                cursor.execute(query_principals, (titleID,))
                title_principals = cursor.fetchall()
                
                if title_principals:
                    movie['principals'] = [{'nameID': str(principal[0]), 'name': principal[1], 'category': principal[2], 'image': principal[3]} for principal in title_principals]    

                movie['rating'] = fetch_title_rating(cursor, movie_data[0])

                return jsonify(movie), 200
            
            except Exception as e:
                print("Error in query_akas execution:", str(e))
                return jsonify({"error": "Internal server error"}), 500

        else:
            return jsonify({"error": "Title not found"}), 204
    
    else:
        return jsonify({"error": "Not Available"}), 404

def convert_to_csv_nameObject(json_data):
    # Initialize a StringIO object to write CSV data
    csv_buffer = StringIO()
    
    # Create a CSV writer object
    writer = csv.writer(csv_buffer)
    
    # Define fieldnames for CSV headers
    name_basics_fields = ['nameID', 'name', 'namePoster', 'birthYr', 'deathYr', 'profession']
    name_titles_fields = ['nameID', 'titleID', 'category']

    # Write the header row and data rows for title basics
    writer.writerow(['name_basics'])
    writer.writerow(name_basics_fields)
    for principal in json_data:
        writer.writerow([principal[field] for field in name_basics_fields])
    
    # Write a blank row to separate the umbrella titles
    writer.writerow([])

    # Write the header row and data rows for title akas
    writer.writerow(['name_titles'])
    writer.writerow(name_titles_fields)
    for principal in json_data:
        name_title = principal.get('nameTitles')
        if name_title:
            for name_info in name_title:
                writer.writerow([principal['nameID'], name_info['titleID'], name_info['category']])
        else:
            writer.writerow(['N/A'] * len(name_titles_fields))  # Write placeholder values if no title akas are available
    
    # Write a blank row to separate the umbrella titles
    writer.writerow([])
    
    # Get the CSV data as a string
    csv_data = csv_buffer.getvalue()
    
    # Close the StringIO buffer
    csv_buffer.close()
    
    return csv_data

def convert_to_csv_titleObject(json_data):
    # Initialize a StringIO object to write CSV data
    csv_buffer = StringIO()
    
    # Create a CSV writer object
    writer = csv.writer(csv_buffer)
    
    # Define fieldnames for CSV headers
    title_basics_fields = ['titleID', 'type', 'originalTitle', 'titlePoster', 'startYear', 'endYear', 'genres']
    title_akas_fields = ['titleID', 'akas', 'regionAbbrev']
    title_principals_fields = ['titleID', 'nameID', 'name', 'category']
    title_rating_fields = ['titleID', 'averageRating', 'numVotes']

    # Write the header row and data rows for title basics
    writer.writerow(['title_basics'])
    writer.writerow(title_basics_fields)
    for movie in json_data:
        writer.writerow([movie[field] for field in title_basics_fields])
    
    # Write a blank row to separate the umbrella titles
    writer.writerow([])

    # Write the header row and data rows for title akas
    writer.writerow(['title_Akas'])
    writer.writerow(title_akas_fields)
    for movie in json_data:
        title_akas = movie.get('titleAkas')
        if title_akas:
            for akas_info in title_akas:
                writer.writerow([movie['titleID'], akas_info['titleAkas'], akas_info['regionAbbrev']])
        else:
            writer.writerow(['N/A'] * len(title_akas_fields))  # Write placeholder values if no title akas are available
    
    # Write a blank row to separate the umbrella titles
    writer.writerow([])

    # Write the header row and data rows for title principals
    writer.writerow(['title_principals'])
    writer.writerow(title_principals_fields)
    for movie in json_data:
        title_principals = movie.get('principals')
        if title_principals:
            for principal_info in title_principals:
                writer.writerow([movie['titleID'], principal_info['nameID'], principal_info['name'], principal_info['category']])
        else:
            writer.writerow(['N/A'] * len(title_principals_fields))  # Write placeholder values if no title principals are available

    # Write a blank row to separate the umbrella titles
    writer.writerow([])
    
    # Write the header row and data rows for title rating
    writer.writerow(['title_rating'])
    writer.writerow(title_rating_fields)
    for movie in json_data:
        title_rating = movie.get('rating')
        if title_rating:
            writer.writerow([movie['titleID'], title_rating['avRating'], title_rating['numVotes']])
        else:
            writer.writerow(['N/A'] * len(title_rating_fields))  # Write placeholder values if no title rating is available
    
    # Get the CSV data as a string
    csv_data = csv_buffer.getvalue()
    
    # Close the StringIO buffer
    csv_buffer.close()
    
    return csv_data

@app.route('/ntuaflix_api/movie_reviews/<int:titleID>', methods=['GET'])
def get_user_reviews_by_movie(titleID):
    # SQL query to join user_rating with users on userid and filter by title_basicstconst
 try:
    sql_query = f"""
    SELECT u.Username, ur.rating, ur.comment
    FROM user_ratings ur
    JOIN users u ON ur.usersid = u.id
    WHERE ur.title_basicstconst = {titleID}
    """
    # Execute the query
    cursor = db.cursor()
    cursor.execute(sql_query)
    
    # Fetch all the results
    results = cursor.fetchall()
    
    # Optionally, convert results to a more readable format
    reviews = [{'username': row[0], 'rating': row[1], 'comment': row[2]} for row in results]
#  except mysql.DatabaseError as e:
#         # Handle database-related errors, e.g., connection issues, SQL errors
#         print(f"Database error: {e}")
#         reviews = []  # Return an empty list or you could also choose to re-raise the exception
 except Exception as e:
        # Handle other possible errors
        print(f"An error occurred: {e}")
        reviews = []  # Return an empty list or re-raise the exception
 finally:
        # Ensure the database connection is closed properly
        cursor.close()
    
 return reviews


@app.route('/ntuaflix_api/admin/upload/titlebasics', methods=['POST'])
def upload_title_basics():
    if request.method == 'POST':
            cursor = db.cursor()
            try:
                file = request.files['file']
                max_file_size_kb = 1024
                if file and file.content_length and file.content_length > max_file_size_kb * 1024:
                    return jsonify({"error": "File size exceeds the allowed limit."}), 400
                # Read the TSV file
                content = file.read().decode('utf-8').splitlines()

                # Skip the first line (header)
                iter_content = iter(content)
                next(iter_content)
                
                for line in iter_content:
                    values = line.split('\t')
                    tconst, titleType, primaryTitle, originalTitle, isAdult, startYear, endYear, runtimeMinutes, genres, img_url_asset = values
                    
                    endYear = 'NULL' if endYear == '\\N' else endYear
                    runtimeMinutes = 'NULL' if runtimeMinutes == '\\N' else runtimeMinutes                
                    genres = 'NULL' if genres == '\\N' else genres
                    img_url_asset = 'NULL' if img_url_asset == '\\N' else img_url_asset  
                    primaryTitle = primaryTitle.replace("'", "''")
                    originalTitle = originalTitle.replace("'", "''")

                    tconst = int(tconst[2:])
                    query_insert = f"INSERT INTO title_basics (tconst, titleType, primaryTitle, originalTitle, isAdult, startYear, endYear, runtimeMinutes, genres, img_url_asset) VALUES ({tconst}, '{titleType}', '{primaryTitle}', '{originalTitle}', {isAdult}, {startYear}, {endYear}, {runtimeMinutes}, '{genres}', '{img_url_asset}')"
                    cursor.execute(query_insert)

                db.commit()

                return jsonify({"message": "Data successfully uploaded."}), 200
            
            except IntegrityError as e:
            # Handle duplicate key error
                db.rollback()
                return jsonify({"error": f"Duplicate Key: {str(e)}"}), 500

            except Exception as e:
                return jsonify({"error": str(e)}), 500

            finally:
                cursor.close()
    else:
        return jsonify({"error": "Not available"}), 404
    
from mysql.connector import IntegrityError  # Replace with the appropriate library

@app.route('/ntuaflix_api/admin/upload/titleakas', methods=['POST'])
def upload_title_akas():
    if request.method == 'POST':
        cursor = db.cursor()
        try:
            file = request.files['file']
            max_file_size_kb = 1024
            if file and file.content_length and file.content_length > max_file_size_kb * 1024:
                return jsonify({"error": "File size exceeds the allowed limit."}), 400
            # Read the TSV file
            content = file.read().decode('utf-8').splitlines()

            # Skip the first line (header)
            iter_content = iter(content)
            next(iter_content)

            for line in iter_content:
                values = line.split('\t')
                titleId, ordering, title, region, language, types, attributes, isOriginalTitle = values
                
                region = 'NULL' if region == '\\N' else region
                language = 'NULL' if language == '\\N' else language
                types = 'NULL' if types == '\\N' else types
                attributes = 'NULL' if attributes == '\\N' else attributes

                titleId = int(titleId[2:])
                title = title.replace("'", "''")

                # Use parameterized query to avoid SQL injection
                query_insert = """
                    INSERT INTO title_akas (titleId, ordering, title, region, language, types, attributes, isOriginalTitle)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query_insert, (titleId, ordering, title, region, language, types, attributes, isOriginalTitle))

            db.commit()

            return jsonify({"message": "Data successfully uploaded."}), 200

        except IntegrityError as e:
            # Handle duplicate key error
            db.rollback()
            return jsonify({"error": f"Duplicate Key: {str(e)}"}), 500

        except Exception as e:
            return jsonify({"error": str(e)}), 500

        finally:
            cursor.close()
    else:
        return jsonify({"error": "Not available"}), 404

@app.route('/ntuaflix_api/admin/upload/titlecrew', methods=['POST'])
def upload_title_crew():
    if request.method == 'POST':
        cursor = db.cursor()
        try:
            file = request.files['file']
            max_file_size_kb = 1024
            if file and file.content_length and file.content_length > max_file_size_kb * 1024:
                return jsonify({"error": "File size exceeds the allowed limit."}), 400
            # Read the TSV file
            content = file.read().decode('utf-8').splitlines()
            # Skip the first line (header)
            iter_content = iter(content)
            next(iter_content)
            
            directors_query = """
                INSERT INTO director (name_basicsnconst, title_basicstconst)
                VALUES (%s, %s)
            """
            
            writers_query = """
                INSERT INTO writer (name_basicsnconst, title_basicstconst)
                VALUES (%s, %s)
            """

            for line in iter_content:
                values = line.split('\t')
                tconst, directors, writers = values

                directors = [nconst[2:] for nconst in (directors.split(',') if directors else [])]
                writers = [nconst[2:] for nconst in (writers.split(',') if writers else [])]
                tconst = int(tconst[2:])

                for nconst in directors:
                    nconst = int(nconst) if nconst else None
                    print(f"Attempting to insert director with nconst: {nconst} and tconst: {tconst}")
                    cursor.execute(directors_query, (nconst, tconst))

                for nconst in writers:
                    nconst = int(nconst) if nconst else None
                    print(f"Attempting to insert writer with nconst: {nconst} and tconst: {tconst}")
                    cursor.execute(writers_query, (nconst, tconst))

            db.commit()

            return jsonify({"message": "Data successfully uploaded."}), 200
        except IntegrityError as e:
            # Handle duplicate key error
            db.rollback()
            return jsonify({"error": f"Duplicate Key: {str(e)}"}), 500
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
    else:
        return jsonify({"error": "Not available"}), 404
    
@app.route('/ntuaflix_api/admin/upload/titleepisode', methods=['POST'])
def upload_title_episode():
    if request.method == 'POST':
        cursor = db.cursor()
        try:
            file = request.files['file']
            max_file_size_kb = 1024
            if file and file.content_length and file.content_length > max_file_size_kb * 1024:
                return jsonify({"error": "File size exceeds the allowed limit."}), 400

            # Read the TSV file
            content = file.read().decode('utf-8').splitlines()

            # Skip the first line (header)
            iter_content = iter(content)
            next(iter_content)
            
            for line in iter_content:
                values = line.split('\t')
                tconst, parentTconst, seasonNumber, episodeNumber = values

                tconst = int(tconst[2:])
                parentTconst = int(parentTconst[2:])
                seasonNumber = int(seasonNumber) if seasonNumber != '\\N' else None
                episodeNumber = int(episodeNumber) if episodeNumber != '\\N' else None

                query_insert = "INSERT INTO title_episode (tconst, parentTconst, seasonNumber, episodeNumber) VALUES (%s, %s, %s, %s)"
                cursor.execute(query_insert, (tconst, parentTconst, seasonNumber, episodeNumber))
            db.commit()

            return jsonify({"message": "Data successfully uploaded."}), 200
        except IntegrityError as e:
            # Handle duplicate key error
            db.rollback()
            return jsonify({"error": f"Duplicate Key: {str(e)}"}), 500

        except Exception as e:
            return jsonify({"error": str(e)}), 500

        finally:
            cursor.close()
    else:
        return jsonify({"error": "Not available"}), 404

@app.route('/ntuaflix_api/admin/upload/namebasics', methods=['POST'])
def upload_name_basics():
    if request.method == 'POST':
        cursor = db.cursor()
        try:
            file = request.files['file']
            max_file_size_kb = 1024
            if file and file.content_length and file.content_length > max_file_size_kb * 1024:
                return jsonify({"error": "File size exceeds the allowed limit."}), 400

            # Read the TSV file
            content = file.read().decode('utf-8').splitlines()

            # Skip the first line (header)
            iter_content = iter(content)
            next(iter_content)

            for line in iter_content:
                values = line.split('\t')
                nconst, primaryName, birthYear, deathYear, primaryProfession, knownForTitles, img_url_asset = values
                nconst = int(nconst[2:])
                knownForTitles = [tconst[2:] for tconst in knownForTitles.split(',')]
                birthYear = int(birthYear) if birthYear != '\\N' else None
                deathYear = int(deathYear) if deathYear != '\\N' else None

                # Insert into name_basics using parameterized query
                name_basics_query = """
                INSERT INTO name_basics (nconst, primaryName, birthYear, deathYear, primaryProfession, img_url_asset)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(name_basics_query, (nconst, primaryName, birthYear, deathYear, primaryProfession, img_url_asset))

                # Insert into knownForTitles using parameterized query with tconst as integer
                if knownForTitles:
                    knownForTitles_query = """
                    INSERT INTO knownfortitles (name_basicsnconst, title_basicstconst)
                    VALUES (%s, %s)
                    """
                    for tconst in knownForTitles:
                        tconst_int = int(tconst) if tconst else None
                        cursor.execute(knownForTitles_query, (nconst, tconst_int if tconst_int is not None else 0))

            db.commit()

            return jsonify({"message": "Data successfully uploaded."}), 200
        except IntegrityError as e:
                # Handle duplicate key error
            db.rollback()
            return jsonify({"error": f"Duplicate Key: {str(e)}"}), 500

        except Exception as e:
            return jsonify({"error": str(e)}), 500

        finally:
            cursor.close()
    else:
        return jsonify({"error": "Not available"}), 404

@app.route('/ntuaflix_api/admin/upload/titleprincipals', methods=['POST'])
def upload_title_principals():
    if request.method == 'POST':
        cursor = db.cursor()
        try:
            file = request.files['file']
            file_content = file.read().decode('utf-8')
            app.logger.info(f"File content: {file_content}")
            
            max_file_size_kb = 1024
            if file and file.content_length and file.content_length > max_file_size_kb * 1024:
                return jsonify({"error": "File size exceeds the allowed limit."}), 400

            # Read the TSV file
            content = file_content.splitlines()

            # Skip the first line (header)
            iter_content = iter(content)
            next(iter_content)
            title_principals_query = """
                INSERT INTO title_principals (tconst, ordering, name_basicsnconst, category, job, characters, img_url_asset)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            for line in iter_content:
                values = line.split('\t')
                tconst, ordering, nconst, category, job, characters, img_url_asset = values
                tconst = int(tconst[2:])
                nconst = int(nconst[2:])

                job = None if job == '\\N' else job
                characters = None if characters == '\\N' else characters
                img_url_asset = None if img_url_asset == '\\N' else img_url_asset

                # Insert into name_basics using parameterized query
                cursor.execute(title_principals_query, (tconst, ordering, nconst, category, job, characters, img_url_asset))
            
            db.commit()
            return jsonify({"message": "Data successfully uploaded."}), 200

        except IntegrityError as e:
            # Handle duplicate key error
            db.rollback()
            return jsonify({"error": f"Duplicate Key: {str(e)}"}), 500

        except Exception as e:
            print({"error": str(e)})
            return jsonify({"error": str(e)}), 500

        finally:
            cursor.close()
    else:
        return jsonify({"error": "Not available"}), 404

@app.route('/ntuaflix_api/admin/upload/titleratings', methods=['POST'])
def upload_title_ratings():
    if request.method == 'POST':
            cursor = db.cursor()
            try:
                file = request.files['file']
                max_file_size_kb = 1024
                if file and file.content_length and file.content_length > max_file_size_kb * 1024:
                    return jsonify({"error": "File size exceeds the allowed limit."}), 400
                # Read the TSV file
                content = file.read().decode('utf-8').splitlines()

                # Skip the first line (header)
                iter_content = iter(content)
                next(iter_content)
                
                for line in iter_content:
                    values = line.split('\t')
                    tconst, averageRating, numVotes= values

                    tconst = int(tconst[2:])
                    query_insert = f"INSERT INTO title_ratings (tconst, averageRating, numVotes) VALUES ({tconst}, {averageRating}, {numVotes})"
                    cursor.execute(query_insert)

                db.commit()

                return jsonify({"message": "Data successfully uploaded."}), 200
            
            except IntegrityError as e:
                # Handle duplicate key error
                db.rollback()
                return jsonify({"error": f"Duplicate Key: {str(e)}"}), 500

            except Exception as e:
                return jsonify({"error": str(e)}), 500

            finally:
                cursor.close()
    else:
        return jsonify({"error": "Not available"}), 404
    
    
@app.route('/ntuaflix_api/admin/usermod/<username>/<password>', methods=['POST'])
def usermod(username, password):
    if request.method == 'POST':
        try:
            cursor = db.cursor()
            query_check = "SELECT * FROM users WHERE Username = %s"
            cursor.execute(query_check,(username,))
            user = cursor.fetchone()
            if user:
                query = "UPDATE users SET password = %s WHERE Username = %s"
                cursor.execute(query, (password, username))
            else:
                query = "INSERT INTO users (Username, password, is_admin) VALUES (%s, %s, 0)"
                cursor.execute(query, (username, password))

            db.commit()
            return jsonify({"message": "User modification successful"}), 200

        except Exception as e:
            # Handle errors
            print(str(e))
            return jsonify({"error": "Internal server error"}), 500
        
        finally:
            cursor.close()

    else:
        return jsonify({"error": "Not available"}), 404
    
@app.route('/ntuaflix_api/admin/users/<username>', methods=['POST'])
def users(username):
    if request.method == 'POST':
        try:
            cursor = db.cursor()
            query_check = "SELECT * FROM users WHERE Username = %s"
            cursor.execute(query_check,(username,))
            user = cursor.fetchone()
            if user:
                user_data = {
                    'id': user[0],
                    'username': user[1],
                }
                return jsonify({"User Data": user_data}), 200
            else:
                return jsonify({"message": "User not found"}), 204

        except Exception as e:
            # Handle errors
            print(str(e))
            return jsonify({"error": "Internal server error"}), 500

    else:

        return jsonify({"error": "Not available"}), 404   

if __name__ == '__main__':
    app.run(debug=True, port=9876, ssl_context=('cert.pem', 'key.pem'), host='127.0.0.1')