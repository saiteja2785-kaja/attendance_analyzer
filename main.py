import pandas as pd

TARGET = 75   # percent, must be below 100
FUTURE = 10   # upcoming classes for projections
CUSTOM_ATTEND = 9  # classes you expect to attend out of FUTURE



def load(path):
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        raise ValueError(f"File not found: {path}")
    except pd.errors.EmptyDataError:
        raise ValueError("The CSV file is empty.")
    except pd.errors.ParserError:
        raise ValueError("The CSV file is malformed.")

    if df.empty:
        raise ValueError("No student records found in the CSV.")

    required = [
        "student_id",
        "name",
        "total_classes",
        "attended_classes",
    ]

    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    if df[required].isnull().any().any():
        raise ValueError("Missing values found in the CSV.")

    if df["student_id"].duplicated().any():
        raise ValueError("Duplicate student IDs found.")

    for c in ["total_classes", "attended_classes"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

        if df[c].isnull().any() or (df[c] % 1 != 0).any():
            raise ValueError(f"{c} must contain whole numbers.")

        df[c] = df[c].astype(int)

    if (df["total_classes"] <= 0).any():
        raise ValueError("total_classes must be greater than 0.")

    if (df["attended_classes"] < 0).any():
        raise ValueError("attended_classes cannot be negative.")

    if (df["attended_classes"] > df["total_classes"]).any():
        raise ValueError(
            "attended_classes cannot exceed total_classes."
        )

    return df


def classes_needed(a, t, target):
    if a * 100 >= target * t:
        return 0
    n = target * t - 100 * a
    d = 100 - target
    return -(-n // d)  # integer ceiling
def safe_to_miss(a, t, target):
    if a * 100 < target * t:
        return 0
    return (100 * a - target * t) // target


def analyze(df, target, future, custom_attend):
    if not (0 < target < 100):
        raise SystemExit("TARGET must be between 0 and 100 (exclusive)")
    if not (0 <= custom_attend <= future):
        raise SystemExit("CUSTOM_ATTEND must be between 0 and FUTURE")
    a, t = df["attended_classes"], df["total_classes"]
    df["attendance_pct"] = (a / t * 100).round(2)
    df["status"] = ["Target met" if x * 100 >= target * y else "Shortage"
                    for x, y in zip(a, t)]
    df["classes_needed"] = [classes_needed(x, y, target) for x, y in zip(a, t)]
    df["proj_attend_all"] = ((a + future) / (t + future) * 100).round(2)
    df["proj_miss_all"] = (a / (t + future) * 100).round(2)
    df["proj_custom"] = ((a + custom_attend) / (t + future) * 100).round(2)
    
    df["safe_to_miss"] = [safe_to_miss(x, y, target) for x, y in zip(a, t)]
    return df
def ask_custom(future):
    while True:
        text = input(f"Classes you expect to attend out of the next {future} (0 to {future}): ")
        try:
            value = int(text)
        except ValueError:
            print("Please enter a whole number.")
            continue
        if 0 <= value <= future:
            return value
        print(f"Number must be between 0 and {future}.")


if __name__ == "__main__":
    custom = ask_custom(FUTURE)
    result = analyze(load("attendance.csv"), TARGET, FUTURE, custom)
    print(result.to_string(index=False))
    result.to_csv("attendance_report.csv", index=False)
    print("\nReport saved to attendance_report.csv")