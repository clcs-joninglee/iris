import requests
import csv
import io
from iris.database import SessionLocal
from iris.models.iris import Iris

URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"

SPECIES_MAP = {
    "Iris-setosa": "setosa",
    "Iris-versicolor": "versicolor",
    "Iris-virginica": "virginica",
}

def crawl():
    print("Fetching Iris data...")
    res = requests.get(URL, timeout=10)
    res.raise_for_status()

    db = SessionLocal()
    count = 0
    reader = csv.reader(io.StringIO(res.text))
    for row in reader:
        if len(row) != 5:
            continue
        db.add(Iris(
            SepalLengthCm=float(row[0]),
            SepalWidthCm=float(row[1]),
            PetalLengthCm=float(row[2]),
            PetalWidthCm=float(row[3]),
            Species=SPECIES_MAP[row[4]],
        ))
        count += 1
    db.commit()
    db.close()
    print(f"Done! {count} records inserted.")

if __name__ == "__main__":
    crawl()