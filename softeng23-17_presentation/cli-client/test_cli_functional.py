import json
from click.testing import CliRunner
from cli import cli  

def test_login_functional():
    runner = CliRunner()
    result = runner.invoke(
        cli, ["login", "--username", "admin", "--password", "0"]
    )
    assert result.exit_code == 0
    assert "{'is_admin': 1, 'user_id': 5, 'username': 'admin'}" in result.output

def test_title_functional():
    runner = CliRunner()
    result = runner.invoke(
        cli, ["title", "--titleID", 929]
    )
    assert result.exit_code == 0
    assert "929" in result.output

def test_searchtitle_functional():
    runner = CliRunner()
    result = runner.invoke(
        cli, ["searchtitle", "--titlepart", "Air America"]
    )
    assert result.exit_code == 0
    assert "Air America" in result.output

def test_bygenre_functional():
    runner = CliRunner()
    result = runner.invoke(
        cli, ["bygenre", "--genre", "Comedy", "--min", 5.2, "--start", 1990, "--end", 2000]
    )
    assert result.exit_code == 0

def test_name_functional():
    runner = CliRunner()
    result = runner.invoke(
        cli, ["name", "--nameID", 1]
    )
    assert result.exit_code == 0
    assert "1" in result.output

def test_searchname_functional():
    runner = CliRunner()
    result = runner.invoke(
        cli, ["searchname", "--namepart", "James"]
    )
    assert result.exit_code == 0
    assert "James" in result.output

def test_heathcheck_functional():
    runner = CliRunner()
    result = runner.invoke(
        cli, ["healthcheck"]
    )
    assert result.exit_code == 0
    assert "'status': 'OK'"  in result.output

def test_newtitles_functional():
    runner = CliRunner()
    result = runner.invoke(
        cli, ["newtitles", "--filename" , "/Users/mariasabani/Desktop/Notes-Assignments/ΤΛ/truncated_data3/truncated_title.basics.tsv"]
    )
    assert result.exit_code == 0
    assert "'Only admin can upload files'" not in result.output

def test_newnames_functional():
    runner = CliRunner()
    result = runner.invoke(
        cli, ["newnames", "--filename" , "/Users/mariasabani/Desktop/Notes-Assignments/ΤΛ/truncated_data3/truncated_name.basics.tsv"]
    )
    assert result.exit_code == 0

def test_newprincipals_functional():
    runner = CliRunner()
    result = runner.invoke(
        cli, ["newprincipals", "--filename" , "/Users/mariasabani/Desktop/Notes-Assignments/ΤΛ/truncated_data3/truncated_title.principals.tsv"]
    )
    assert result.exit_code == 0
    assert "'Only admin can upload files'" not in result.output

def test_newcrew_functional():
    runner = CliRunner()
    result = runner.invoke(
        cli, ["newcrew", "--filename" , "/Users/mariasabani/Desktop/Notes-Assignments/ΤΛ/truncated_data3/truncated_title.crew.tsv"]
    )
    assert result.exit_code == 0
    assert "'Only admin can upload files'" not in result.output

def test_newepisode_functional():
    runner = CliRunner()
    result = runner.invoke(
        cli, ["newepisode", "--filename" , "/Users/mariasabani/Desktop/Notes-Assignments/ΤΛ/truncated_data3/truncated_title.episode.tsv"]
    )
    assert result.exit_code == 0
    assert "'Only admin can upload files'" not in result.output

def test_newakas_functional():
    runner = CliRunner()
    result = runner.invoke(
        cli, ["newakas", "--filename" , "/Users/mariasabani/Desktop/Notes-Assignments/ΤΛ/truncated_data3/truncated_title.akas.tsv"]
    )
    assert result.exit_code == 0
    assert "'Only admin can upload files'" not in result.output

def test_newratings_functional():
    runner = CliRunner()
    result = runner.invoke(
        cli, ["newratings", "--filename" , "/Users/mariasabani/Desktop/Notes-Assignments/ΤΛ/truncated_data3/truncated_title.ratings.tsv"]
    )
    assert result.exit_code == 0
    assert "'Only admin can upload files'" not in result.output

def test_adduser_functional():
    runner = CliRunner()
    result = runner.invoke(
        cli, ["adduser", "--username" , "mar", "--passw", "5"]
    )
    assert result.exit_code == 0
    assert "'User modification successful'" in result.output

def test_user_functional():
    runner = CliRunner()
    result = runner.invoke(
        cli, ["user", "--username" , "mar"]
    )
    assert result.exit_code == 0
    assert 'mar' in result.output
