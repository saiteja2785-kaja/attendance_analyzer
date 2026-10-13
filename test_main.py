import pandas as pd
import pytest

from main import load, classes_needed, analyze
from main import load, classes_needed, analyze, safe_to_miss

def one_student(total, attended):
    return pd.DataFrame({
        "student_id": [1],
        "name": ["Test"],
        "total_classes": [total],
        "attended_classes": [attended],
    })


def write_csv(tmp_path, text):
    path = tmp_path / "data.csv"
    path.write_text(text)
    return str(path)


# ---- classes_needed ----
def test_classes_needed_shortage():
    assert classes_needed(70, 100, 75) == 20
    assert classes_needed(30, 50, 75) == 30


def test_classes_needed_already_met():
    assert classes_needed(90, 100, 75) == 0
    assert classes_needed(60, 80, 75) == 0  # exactly 75%


def test_classes_needed_is_the_minimum():
    x = classes_needed(70, 100, 75)
    assert (70 + x) * 100 >= 75 * (100 + x)              # reaches target
    assert (70 + x - 1) * 100 < 75 * (100 + x - 1)       # one fewer does not


# ---- analyze ----
def test_analyze_values_for_priya():
    row = analyze(one_student(100, 70), 75, 10, 8).iloc[0]
    assert row["attendance_pct"] == pytest.approx(70.0)
    assert row["status"] == "Shortage"
    assert row["classes_needed"] == 20
    assert row["proj_attend_all"] == pytest.approx(72.73)
    assert row["proj_miss_all"] == pytest.approx(63.64)
    assert row["proj_custom"] == pytest.approx(70.91)


def test_analyze_exactly_75_is_target_met():
    row = analyze(one_student(80, 60), 75, 10, 5).iloc[0]
    assert row["status"] == "Target met"


def test_analyze_rejects_target_100():
    with pytest.raises(SystemExit):
        analyze(one_student(100, 70), 100, 10, 5)


def test_analyze_rejects_bad_custom():
    with pytest.raises(SystemExit):
        analyze(one_student(100, 70), 75, 10, 11)


# ---- load (validation) ----
def test_load_valid_file(tmp_path):
    path = write_csv(tmp_path, "student_id,name,total_classes,attended_classes\n1,A,10,8\n")
    assert len(load(path)) == 1


def test_load_rejects_attended_over_total(tmp_path):
    path = write_csv(tmp_path, "student_id,name,total_classes,attended_classes\n1,A,10,12\n")
    with pytest.raises(SystemExit):
        load(path)


def test_load_rejects_duplicate_ids(tmp_path):
    path = write_csv(tmp_path, "student_id,name,total_classes,attended_classes\n1,A,10,8\n1,B,10,7\n")
    with pytest.raises(SystemExit):
        load(path)


def test_load_rejects_missing_column(tmp_path):
    path = write_csv(tmp_path, "student_id,name,total_classes\n1,A,10\n")
    with pytest.raises(SystemExit):
        load(path)


def test_load_missing_file():
    with pytest.raises(SystemExit):
        load("does_not_exist.csv")

# ---- safe_to_miss ----
def test_safe_to_miss_values():
    assert safe_to_miss(90, 100, 75) == 20
    assert safe_to_miss(100, 120, 75) == 13
    assert safe_to_miss(60, 80, 75) == 0   # exactly 75%, no room
    assert safe_to_miss(70, 100, 75) == 0  # already short


def test_safe_to_miss_is_the_maximum():
    m = safe_to_miss(100, 120, 75)
    assert 100 * 100 >= 75 * (120 + m)        # still at target
    assert 100 * 100 < 75 * (120 + m + 1)     # one more miss drops below