import subprocess
import sys


def test_parser(tmp_path):
    csvfile = tmp_path / "report.csv"
    jsonfile = tmp_path / "report.json"

    result = subprocess.run([
        sys.executable, "parser.py", "file",
        "samples/failedlogons.txt",
        str(csvfile), str(jsonfile)
    ])

    assert result.returncode == 0
    assert csvfile.exists()
    assert jsonfile.exists()


def test_empty_file(tmp_path):
    logfile = tmp_path / "empty.txt"
    logfile.write_text("")

    result = subprocess.run([
        sys.executable, "parser.py", "file",
        str(logfile),
        str(tmp_path / "report.csv"),
        str(tmp_path / "report.json")
    ])

    assert result.returncode == 0


def test_api_failure(tmp_path):
    result = subprocess.run([
        "python", "parser.py", "api",
        "http://127.0.0.1:1",
        str(tmp_path / "report.csv"),
        str(tmp_path / "report.json")
    ])

    assert result.returncode == 1