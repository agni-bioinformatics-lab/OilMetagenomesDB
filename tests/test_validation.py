"""Tests for the validation scripts in scripts/.

The fixture tables in tests/data/ are three real rows of each table; invalid
cases are made by changing one value in a copy of them.
"""
import os
import subprocess
import sys

import pandas as pd
import pytest

import validation_libraries
import validation_samples
import validation_srs

from conftest import REPO_ROOT


def read(path):
    return validation_samples.read_dataframe_for_validation(path)


def write(df, path):
    df.to_csv(path, sep="\t", index=False)
    return str(path)


# --- JSON schema validation of individual values ---------------------------

def test_valid_sample_rows_pass_schemas(samples_path, schemas_samples):
    results, has_errors = validation_samples.validate_new_rows(read(samples_path), schemas_samples, 0)
    assert results == {}
    assert has_errors is False


def test_valid_library_rows_pass_schemas(libraries_path, schemas_libraries):
    results, has_errors = validation_libraries.validate_new_rows(read(libraries_path), schemas_libraries, 0)
    assert results == {}
    assert has_errors is False


@pytest.mark.parametrize("column, value", [
    ("geo_loc_name", "Atlantis"),          # not in the country list
    ("material", "lava"),                  # not in the controlled vocabulary
    ("temp", "40"),                        # numbers must have a decimal part
    ("temp", "unknownn"),                  # misspelled missing-value marker
    ("archive_accession", "SAMN0001"),     # must start with SRS or ERS
    ("publication_doi", "doi.org/10.1000/x"),
])
def test_invalid_sample_value_is_reported(samples_path, schemas_samples, column, value):
    df = read(samples_path)
    df.loc[1, column] = value
    results, has_errors = validation_samples.validate_new_rows(df, schemas_samples, 0)
    assert has_errors is True
    assert list(results) == [column]
    # Row numbers in messages are file line numbers: header is line 1
    assert results[column][0].startswith("Invalid (Row 3)")


@pytest.mark.parametrize("column, value", [
    ("library_strategy", "shotgun"),
    ("archive_data_accession", "XRR123"),
    ("library_layout", "triple"),
])
def test_invalid_library_value_is_reported(libraries_path, schemas_libraries, column, value):
    df = read(libraries_path)
    df.loc[0, column] = value
    results, has_errors = validation_libraries.validate_new_rows(df, schemas_libraries, 0)
    assert has_errors is True
    assert list(results) == [column]


# --- Table-level checks ----------------------------------------------------

def test_duplicate_rows_are_found(samples_path):
    df = read(samples_path)
    df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
    groups = validation_samples.find_duplicate_rows(df)
    assert list(groups.values()) == [[2, 5]]


def test_no_duplicates_in_fixture(samples_path):
    assert validation_samples.find_duplicate_rows(read(samples_path)) == {}


def test_non_unique_library_columns_are_found(libraries_path):
    df = read(libraries_path)
    df.loc[1, "download_md5s"] = df.loc[0, "download_md5s"]
    found = validation_libraries.check_column_uniqueness(df, ["download_links", "download_md5s"])
    assert dict(found) == {"download_md5s": [2, 3]}


def test_changed_old_row_is_detected(samples_path):
    base = validation_samples.read_dataframe_for_compare(samples_path)
    pr = base.copy()
    pr.loc[0, "depth"] = "1.0"
    diff = validation_samples.compare_dataframes(pr, base)
    assert list(diff.index) == [2]


def test_appended_rows_do_not_count_as_changes(samples_path):
    full = validation_samples.read_dataframe_for_compare(samples_path)
    base = full.iloc[:2]
    assert validation_samples.compare_dataframes(full, base).empty


def test_srs_consistent(samples_path, libraries_path):
    ok, _ = validation_srs.check_srs(read(samples_path)["archive_accession"],
                                     read(libraries_path)["archive_accession"])
    assert ok


def test_srs_mismatch_in_both_directions(samples_path, libraries_path):
    samples = read(samples_path)["archive_accession"].copy()
    libraries = read(libraries_path)["archive_accession"].copy()
    samples[0] = "SRS0000001"
    ok, message = validation_srs.check_srs(samples, libraries)
    assert not ok
    assert "SRS0000001 is not in libraries" in message
    assert "is not in samples" in message


# --- Command-line runs with a base file (no git, no network) --------------

def run_samples(table, base, schemas):
    validation_samples.main(["--table", table, "--base-file", base, "--schemas", schemas])


def test_cli_accepts_valid_appended_row(tmp_path, samples_path, schemas_samples):
    full = read(samples_path)
    base = write(full.iloc[:2], tmp_path / "base.tsv")
    run_samples(samples_path, base, schemas_samples)  # no SystemExit


def test_cli_rejects_invalid_appended_row(tmp_path, samples_path, schemas_samples, capsys):
    full = read(samples_path)
    base = write(full.iloc[:2], tmp_path / "base.tsv")
    full.loc[2, "geo_loc_name"] = "Atlantis"
    table = write(full, tmp_path / "pr.tsv")
    with pytest.raises(SystemExit) as exit_info:
        run_samples(table, base, schemas_samples)
    assert exit_info.value.code == 1
    assert "Invalid (Row 4)" in capsys.readouterr().out


def test_cli_rejects_changed_old_row(tmp_path, samples_path, schemas_samples, capsys):
    full = read(samples_path)
    base = write(full.iloc[:2], tmp_path / "base.tsv")
    full.loc[0, "temp"] = "99.0"
    table = write(full, tmp_path / "pr.tsv")
    with pytest.raises(SystemExit) as exit_info:
        run_samples(table, base, schemas_samples)
    assert exit_info.value.code == 1
    assert "old rows have been changed" in capsys.readouterr().out


def test_cli_rejects_duplicate_appended_row(tmp_path, samples_path, schemas_samples, capsys):
    full = read(samples_path)
    base = write(full, tmp_path / "base.tsv")
    table = write(pd.concat([full, full.iloc[[0]]], ignore_index=True), tmp_path / "pr.tsv")
    with pytest.raises(SystemExit) as exit_info:
        run_samples(table, base, schemas_samples)
    assert exit_info.value.code == 1
    assert "Duplicate rows exist" in capsys.readouterr().out


def test_cli_rejects_non_unique_library_column(tmp_path, libraries_path, schemas_libraries, capsys):
    full = read(libraries_path)
    base = write(full.iloc[:2], tmp_path / "base.tsv")
    full.loc[2, "download_md5s"] = full.loc[0, "download_md5s"]
    table = write(full, tmp_path / "pr.tsv")
    with pytest.raises(SystemExit) as exit_info:
        validation_libraries.main(["--table", table, "--base-file", base, "--schemas", schemas_libraries])
    assert exit_info.value.code == 1
    assert "'download_md5s' has non-unique values" in capsys.readouterr().out


@pytest.mark.xfail(raises=ValueError, strict=True,
                   reason="Deleting rows makes compare_dataframes raise ValueError instead of "
                          "reporting it (task 4.1)")
def test_cli_reports_deleted_row(tmp_path, samples_path, schemas_samples):
    full = read(samples_path)
    table = write(full.iloc[:2], tmp_path / "pr.tsv")
    with pytest.raises(SystemExit):
        run_samples(table, samples_path, schemas_samples)


def test_srs_cli(samples_path, libraries_path):
    validation_srs.main(["--samples", samples_path, "--libraries", libraries_path])  # no SystemExit


# --- Base version from git: must not overwrite the working copy ------------

def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=test", "-c", "user.email=test@example.com",
                    *args], check=True, capture_output=True)


def test_base_ref_reads_git_without_touching_working_tree(tmp_path, samples_path, schemas_samples,
                                                          monkeypatch, capsys):
    repo = tmp_path / "repo"
    (repo / "common_samples").mkdir(parents=True)
    table = repo / "common_samples" / "common_samples.tsv"
    full = read(samples_path)
    write(full.iloc[:2], table)
    git(repo, "init", "-q")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "base")

    full.loc[0, "temp"] = "99.0"   # change an old row in the working copy
    write(full, table)
    edited = table.read_text(encoding="utf-8")

    monkeypatch.chdir(repo)
    with pytest.raises(SystemExit):
        validation_samples.main(["--table", "common_samples/common_samples.tsv",
                                 "--base-ref", "HEAD", "--schemas", schemas_samples])
    assert "old rows have been changed" in capsys.readouterr().out
    assert table.read_text(encoding="utf-8") == edited


# --- Full-table runner ------------------------------------------------------

def run_validate_local(*args):
    return subprocess.run([sys.executable, os.path.join(REPO_ROOT, "scripts", "validate_local.py"), *args],
                          capture_output=True, text=True, cwd=REPO_ROOT)


def test_validate_local_on_fixture(samples_path, libraries_path):
    result = run_validate_local("--samples", samples_path, "--libraries", libraries_path)
    assert result.returncode == 0, result.stdout + result.stderr


def test_validate_local_fails_on_invalid_value(tmp_path, samples_path, libraries_path):
    df = read(samples_path)
    df.loc[0, "pH"] = "seven"
    bad = write(df, tmp_path / "samples.tsv")
    result = run_validate_local("--samples", bad, "--libraries", libraries_path)
    assert result.returncode == 1
    assert '"pH"' in result.stdout


def test_repository_tables_are_valid():
    """Every row of both tables in this checkout conforms to the current schemas."""
    result = run_validate_local()
    assert result.returncode == 0, result.stdout + result.stderr
