import json
import click
import os
from requests import post
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# File paths for session information
SESSION_FILE_PATH = 'session.json'

@click.group()
def cli():
    pass

def save_session(user_id, is_admin):
    session_data = {'user_id': user_id, 'is_admin': is_admin}
    with open(SESSION_FILE_PATH, 'w') as file:
        json.dump(session_data, file)

def load_session():
    if os.path.exists(SESSION_FILE_PATH):
        with open(SESSION_FILE_PATH, 'r') as file:
            return json.load(file)
    return None

def clear_session():
    # Clear the stored session information
    if os.path.exists(SESSION_FILE_PATH):
        os.remove(SESSION_FILE_PATH)


def handle_response(response, format):
    try:
        if response.status_code == 200:
            if format.lower() == 'json':
                try:
                    print(response.json())
                    return response.json()
                except json.decoder.JSONDecodeError as json_err:
                    print(f"Error decoding JSON: {json_err}")
            elif format.lower() == 'csv':
                print(response.content.decode('utf-8'))
                return response.content.decode('utf-8')
            else:
                print(f"Error: Invalid format specified: {format}")
        else:
            print(f"Error: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Error: {e}")

# L O G I N    
@cli.command()
@click.option('--username', prompt='Username', help='The username for login', required=True)
@click.option('--password', prompt=True, hide_input=True, help='The password for login', required=True)
@click.option('--format', help='The desired output format', default='json')
def login(username, password, format):
    url = 'https://127.0.0.1:9876/ntuaflix_api/login' # url from api
    data = {'username': username, 'password': password, 'format': format}

    response = post(url, data=data, verify=False)
    response.raise_for_status()

    user_data = response.json()
    save_session(user_data.get('user_id'), user_data.get('is_admin'))
    response.raise_for_status() 

    handle_response(response, format)


# L O G O U T
@cli.command()
@click.option('--format', help='The desired output format', default='json')
def logout(format):
    session_data = load_session()

    if session_data:
        url = f'https://127.0.0.1:9876/ntuaflix_api/logout'
        data = {'format': format}

        print(f"Sending logout request to {url} with data: {data}")

        response = post(url, data=data, verify=False)

        # Clear the stored session information after the request is made
        clear_session()

        try:
            response.raise_for_status()
            handle_response(response, format)
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
    else:
        print("Error: Not logged in")


# T I T L E
@cli.command()
@click.option('--titleID', prompt='titleID', help='The titleID for searchTitle', required=True)
@click.option('--format', help='The desired output format', default='json')
def title(titleid, format):
    url = f'https://127.0.0.1:9876/ntuaflix_api/title/{titleid}' # url from api
    params = {'format' : format}

    response = requests.get(url, params=params, verify=False)
    response.raise_for_status() # Raises HTTPError, if one occurred.

    handle_response(response, format)

# S E A R C H  B Y  T I T L E
@cli.command()
@click.option('--titlepart', prompt='titlepart', help='The titlepart for searchTitle', required=True)
@click.option('--format', help='The desired output format', default='json')
def searchtitle(titlepart, format):
    url = 'https://127.0.0.1:9876/ntuaflix_api/searchTitle'
    params = {'titlePart': titlepart, 'format': format}

    response = requests.get(url, params=params, verify=False)
    response.raise_for_status() 

    handle_response(response, format)

# S E A R C H  B Y  G E N R E
@cli.command()
@click.option('--genre', prompt='genre', help='The genre of the movie', required=True)
@click.option('--min', prompt='min', help='Minimum Rating of movie', required=True)
@click.option('--start', type=int, help='Start year for filtering titles (optional)')
@click.option('--end', type=int, help='End year for filtering titles (optional)')
@click.option('--format', help='The desired output format', default='json')
def bygenre(genre, min, start, end, format):
    url = 'https://127.0.0.1:9876/ntuaflix_api/bygenre'
    params = {'qgenre': genre, 'minrating': min, 'yrFrom': start, 'yrTo': end, 'format': format}

    response = requests.get(url, params=params, verify=False)
    response.raise_for_status() 

    handle_response(response, format)

# N A M E
@cli.command()
@click.option('--nameID', prompt='nameID', help='The titleID for searchTitle', required=True)
@click.option('--format', help='The desired output format', default='json')
def name(nameid, format):
    url = f'https://127.0.0.1:9876/ntuaflix_api/name/{nameid}'  # URL from API
    params = {'format': format}

    response = requests.get(url, params=params, verify=False)
    response.raise_for_status() 

    handle_response(response, format)

# S E A R C H  N A M E
@cli.command()
@click.option('--namepart', prompt='namepart', help='The titlepart for searchPrincipals', required=True)
@click.option('--format', help='The desired output format', default='json')
def searchname(namepart, format):
    url = 'https://127.0.0.1:9876/ntuaflix_api/searchname' # url from api
    params = {'namePart': namepart, 'format': format}

    response = requests.get(url, params=params, verify=False)
    response.raise_for_status() 

    handle_response(response, format)

# H E A L T H  C H E C K
@cli.command()
@click.option('--format', help='The desired output format', default='json')
def healthcheck(format):
    session_data = load_session()
    if session_data.get('is_admin'):
        url = 'https://127.0.0.1:9876/ntuaflix_api/admin/healthcheck'
        data = {'format': format}
        
        response = requests.get(url, data=data, verify=False)
        response.raise_for_status() 

        handle_response(response, format)
    else:
        print('Only admin can check the database connection')

# R E S E T  A L L
@cli.command()
@click.option('--format', help='The desired output format', default='json')
def resetall(format):
    session_data = load_session()
    if session_data.get('is_admin'):
        url = 'https://127.0.0.1:9876/ntuaflix_api/admin/resetall'
        data = {'format': format}
        
        response = requests.post(url, data=data, verify=False)
        response.raise_for_status() 

        handle_response(response, format)
    else:
        print('Only admin can reset the database')
        

# T I T L E  B A S I C S
@cli.command()
@click.option('--filename', type=click.Path(exists=True), prompt='file', help='The TSV file to upload', required=True)
@click.option('--format', help='The desired output format', default='json')
def newtitles(filename, format):
    session_data = load_session()

    if filename is not None:
        if session_data and session_data.get('is_admin'):
            
            url = 'https://127.0.0.1:9876/ntuaflix_api/admin/upload/titlebasics'  # Replace with your actual API URL
            files = {'file': (filename, open(filename, 'rb'))}
            headers = {'format': format}  # Pass format in headers

            response = requests.post(url, files=files, headers=headers, verify=False)
            handle_response(response, format)
        else:
            print('Only admin can upload files')
    else:
        print("Error: No file provided.")

# N A M E  B A S I C S
@cli.command()
@click.option('--filename', type=click.Path(exists=True), prompt='file', help='The TSV file to upload', required=True)
@click.option('--format', help='The desired output format', default='json')
def newnames(filename, format):
    session_data = load_session()

    if filename is not None:
        if session_data and session_data.get('is_admin'):
            
            url = 'https://127.0.0.1:9876/ntuaflix_api/admin/upload/namebasics'  # Replace with your actual API URL
            files = {'file': (filename, open(filename, 'rb'))}
            headers = {'format': format}  # Pass format in headers

            response = requests.post(url, files=files, headers=headers, verify=False)
            handle_response(response, format)
        else:
            print('Only admin can upload files')
    else:
        print("Error: No file provided.")


# T I T L E  P R I N C I P A L S
@cli.command()
@click.option('--filename', type=click.Path(exists=True), prompt='file', help='The TSV file to upload', required=True)
@click.option('--format', help='The desired output format', default='json')
def newprincipals(filename, format):
    session_data = load_session()

    if filename is not None:
        if session_data and session_data.get('is_admin'):
            
            url = 'https://127.0.0.1:9876/ntuaflix_api/admin/upload/titleprincipals'  # Replace with your actual API URL
            files = {'file': (filename, open(filename, 'rb'))}
            headers = {'format': format}  # Pass format in headers

            response = requests.post(url, files=files, headers=headers, verify=False)
            handle_response(response, format)
        else:
            print('Only admin can upload files')
    else:
        print("Error: No file provided.")

# N E W  C R E W
@cli.command()
@click.option('--filename', type=click.Path(exists=True), prompt='file', help='The TSV file to upload', required=True)
@click.option('--format', help='The desired output format', default='json')
def newcrew(filename, format):
    session_data = load_session()

    if filename is not None:
        if session_data and session_data.get('is_admin'):        
            url = 'https://127.0.0.1:9876/ntuaflix_api/admin/upload/titlecrew'  # Replace with your actual API URL
            files = {'file': (filename, open(filename, 'rb'))}
            headers = {'format': format}  # Pass format in headers

            response = requests.post(url, files=files, headers=headers, verify=False)
            handle_response(response, format)
        else:
            print('Only admin can upload files')
    else:
        print("Error: No file provided.")

# N E W  E P I S O D E
@cli.command()
@click.option('--filename', type=click.Path(exists=True), prompt='file', help='The TSV file to upload', required=True)
@click.option('--format', help='The desired output format', default='json')
def newepisode(filename, format):
    session_data = load_session()

    if filename is not None:
        if session_data and session_data.get('is_admin'):        
            url = 'https://127.0.0.1:9876/ntuaflix_api/admin/upload/titleepisode'  # Replace with your actual API URL
            files = {'file': (filename, open(filename, 'rb'))}
            headers = {'format': format}  # Pass format in headers

            response = requests.post(url, files=files, headers=headers, verify=False)
            handle_response(response, format)
        else:
            print('Only admin can upload files')
    else:
        print("Error: No file provided.")


# T I T L E  A K A S
@cli.command()
@click.option('--filename', type=click.Path(exists=True), prompt='file', help='The TSV file to upload', required=True)
@click.option('--format', help='The desired output format', default='json')
def newakas(filename, format):
    session_data = load_session()

    if filename is not None:
        if session_data and session_data.get('is_admin'):        
            url = 'https://127.0.0.1:9876/ntuaflix_api/admin/upload/titleakas'  # Replace with your actual API URL
            files = {'file': (filename, open(filename, 'rb'))}
            headers = {'format': format}  # Pass format in headers

            response = requests.post(url, files=files, headers=headers, verify=False)
            handle_response(response, format)
        else:
            print('Only admin can upload files')
    else:
        print("Error: No file provided.")

# T I T L E  R A T I N G S
@cli.command()
@click.option('--filename', type=click.Path(exists=True), prompt='file', help='The TSV file to upload', required=True)
@click.option('--format', help='The desired output format', default='json')
def newratings(filename, format):
    session_data = load_session()

    if filename is not None:
        if session_data and session_data.get('is_admin'):            
            url = 'https://127.0.0.1:9876/ntuaflix_api/admin/upload/titleratings'  # Replace with your actual API URL
            files = {'file': (filename, open(filename, 'rb'))}
            headers = {'format': format}  # Pass format in headers

            response = requests.post(url, files=files, headers=headers, verify=False)
            handle_response(response, format)
        else:
            print('Only admin can upload files')
    else:
        print("Error: No file provided.")

# A D D  U S E R
@cli.command()
@click.option('--username', prompt='Username', help='The username of user', required=True)
@click.option('--passw', prompt=True, hide_input=True, help='The password os user', required=True)
@click.option('--format', help='The desired output format', default='json')
def adduser(username, passw, format):
    session_data = load_session()

    if session_data and session_data.get('is_admin'):          
        url = f'https://127.0.0.1:9876/ntuaflix_api/admin/usermod/{username}/{passw}'  # Replace with your actual API URL
        data = {'format': format}
        response = requests.post(url, data=data, verify=False)
        response.raise_for_status() 
        handle_response(response, format)
    else:
        print('Only admin can modify other users')

# S E E  U S E R
@cli.command()
@click.option('--username', prompt='Username', help='The username of user', required=True)
@click.option('--format', help='The desired output format', default='json')
def user(username, format):
    session_data = load_session()

    if session_data and session_data.get('is_admin'):
        url = f'https://127.0.0.1:9876/ntuaflix_api/admin/users/{username}'  # Replace with your actual API URL
        data = {'format': format}
        response = requests.post(url, data=data, verify=False)
        response.raise_for_status() 
        handle_response(response, format)
    else:
        print('Only admin can see other users')
        
if __name__ == '__main__':
    cli()