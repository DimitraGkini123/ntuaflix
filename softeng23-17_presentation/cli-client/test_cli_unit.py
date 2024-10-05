import json
from unittest.mock import patch
import pytest
from click.testing import CliRunner
import requests
from cli import adduser, cli, handle_response, user  # Assuming handle_response is part of your module

class MockResponse:
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content

    def json(self):
        return json.loads(self.content)
    
    def raise_for_status(self):
        if 400 <= self.status_code < 600:
            raise requests.exceptions.HTTPError(f"HTTPError: {self.status_code}")
        
@pytest.fixture
def mock_post(monkeypatch):
    def mock_post_function(url, data=None, verify=None, files = None, headers=None):
        if "login" in url:
            return MockResponse(200, '{"user_id": 5, "is_admin": 1, "username": "admin"}')
        elif "title" in url:
            return MockResponse(200, '{"titleID": 929')
        elif "searchtitle" in url:
            return MockResponse(200, '[{"titlepart": "Air America"}, {"titlepart": "Catchfire"}]')
        elif "bygenre" in url:
            return MockResponse(200, '[{"genre": "Comedy", "min": 5.0}, {"genre": "Drama", "min": 4.0, "start": 1990, "end" 1995}]')
        elif "name" in url:
            return MockResponse(200, '{"nameID": 100}')
        elif "searchname" in url:
            return MockResponse(200, '[{"namepart": "James"}, {"namepart": "Anna"}]')
        elif "healthcheck" in url:
            return MockResponse(200, '[{ "dataconnection": { "charset": "utf8mb4", "collation": "utf8mb4_general_ci", "database": "ntuaflix", "host": "127.0.0.1", "password": "2255", "port": 3306, "user": "root" }, "status": "OK" }]')
        elif "upload/titlebasics" in url:
            return MockResponse(200, '{"message": "Titles uploaded successfully"}')
        elif "upload/namebasics" in url:
            return MockResponse(200, '{"message": "Names uploaded successfully"}')
        elif "upload/titleprincipals" in url:
            return MockResponse(200, '{"message": "Principals uploaded successfully"}')
        elif "upload/titlecrew" in url:
            return MockResponse(200, '{"message": "Crew uploaded successfully"}')
        elif "upload/titleepisode" in url:
            return MockResponse(200, '{"message": "Episode uploaded successfully"}')
        elif "upload/titleakas" in url:
            return MockResponse(200, '{"message": "Akas uploaded successfully"}')
        elif "upload/titleratings" in url:
            return MockResponse(200, '{"message": "Ratings uploaded successfully"}')
        elif "/admin/usermod" in url:
            return MockResponse(200, '{"message": "User modification successful"}')
        elif "/admin/user" in url:
            return MockResponse(200, '{"message": "User data"}')
    monkeypatch.setattr("requests.post", mock_post_function)

def test_handle_response_json():
    response_content = '{"user_id": 1, "is_admin": 0}'
    result = handle_response(MockResponse(200, response_content), 'json')
    assert result == json.loads(response_content)

def test_handle_response_invalid_format():
    response_content = '{"user_id": 1, "is_admin": 0}'
    result = handle_response(MockResponse(200, response_content), 'invalid_format')
    assert result is None  # Adjust based on your actual handling of invalid format

def test_login_unit(mock_post):
    runner = CliRunner()
    result = runner.invoke(cli, ["login", "--username", "admin", "--password", "0"])
    print(result.output)
    assert result.exit_code == 0
    assert "{'is_admin': 1, 'user_id': 5, 'username': 'admin'}" in result.output

def test_title_unit(mock_post):
    runner = CliRunner()
    result = runner.invoke(cli, ["title", "--titleID", "929"])
    assert result.exit_code == 0
    assert "929" in result.output

def test_searchtitle_unit(mock_post):
    runner = CliRunner()
    result = runner.invoke(cli, ["searchtitle", "--titlepart", "Air America"])
    assert result.exit_code == 0
    assert "Air America" in result.output

def test_bygenre_unit(mock_post):
    runner = CliRunner()
    result = runner.invoke(cli, ["bygenre", "--genre", "Comedy", "--min", "5.2", "--start", "1990", "--end", "2000"])
    assert result.exit_code == 0

def test_name_unit(mock_post):
    runner = CliRunner()
    result = runner.invoke(cli, ["name", "--nameID", "100"])
    assert result.exit_code == 0
    assert "100" in result.output

def test_searchname_unit(mock_post):
    runner = CliRunner()
    result = runner.invoke(cli, ["searchname", "--namepart", "James"])
    assert result.exit_code == 0
    assert "James" in result.output

def test_heathcheck_unit(mock_post):
    runner = CliRunner()
    result = runner.invoke(cli, ["healthcheck"])
    assert result.exit_code == 0
    assert "'status': 'OK'"  in result.output

def test_newtitles_unit(mock_post):
    runner = CliRunner()
    result = runner.invoke(cli, ["newtitles", "--filename", "/Users/mariasabani/Desktop/Notes-Assignments/ΤΛ/truncated_data3/truncated_title.basics.tsv", "--format", "json"])
    print(result.output)
    assert result.exit_code == 0


def test_newnames_unit(mock_post):
    runner = CliRunner()
    result = runner.invoke(cli, ["newnames", "--filename", "/Users/mariasabani/Desktop/Notes-Assignments/ΤΛ/truncated_data3/truncated_name.basics.tsv", "--format", "json"])
    print(result.output)
    assert result.exit_code == 0

def test_newprincipals_unit(mock_post):
    runner = CliRunner()
    result = runner.invoke(cli, ["newprincipals", "--filename", "/Users/mariasabani/Desktop/Notes-Assignments/ΤΛ/truncated_data3/truncated_title.principals.tsv", "--format", "json"])
    assert result.exit_code == 0

def test_newcrew_unit(mock_post):
    runner = CliRunner()
    result = runner.invoke(cli, ["newcrew", "--filename", "/Users/mariasabani/Desktop/Notes-Assignments/ΤΛ/truncated_data3/truncated_title.crew.tsv", "--format", "json"])
    assert result.exit_code == 0

def test_newepisode_unit(mock_post):
    runner = CliRunner()
    result = runner.invoke(cli, ["newepisode", "--filename", "/Users/mariasabani/Desktop/Notes-Assignments/ΤΛ/truncated_data3/truncated_title.episode.tsv", "--format", "json"])
    assert result.exit_code == 0

def test_newakas_unit(mock_post):
    runner = CliRunner()
    result = runner.invoke(cli, ["newakas", "--filename", "/Users/mariasabani/Desktop/Notes-Assignments/ΤΛ/truncated_data3/truncated_title.akas.tsv", "--format", "json"])
    assert result.exit_code == 0

def test_newratings_unit(mock_post):
    runner = CliRunner()
    result = runner.invoke(cli, ["newratings", "--filename", "/Users/mariasabani/Desktop/Notes-Assignments/ΤΛ/truncated_data3/truncated_title.ratings.tsv", "--format", "json"])
    assert result.exit_code == 0
    
def test_adduser_unit(mock_post):
    runner = CliRunner()
    result = runner.invoke(cli, ["adduser", "--username", "mar", "--passw", "5", "--format", "json"])
    print(result.output)
    assert result.exit_code == 0
    assert "User modification successful" in result.output

def test_user_unit(mock_post):
    runner = CliRunner()
    result = runner.invoke(cli, ["user", "--username", "mar", "--format", "json"])
    print(result.output)
    assert result.exit_code == 0
    assert "User data" in result.output
