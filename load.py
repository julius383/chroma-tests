import sys

import pandas as pd
from sqlalchemy import create_engine


def into_database(csv, db, table):
    db = create_engine(f"sqlite:///{db}")
    chunksize = 10000
    i = 0
    j = 0
    for df in pd.read_csv(csv, chunksize=chunksize, iterator=True):
        df.index += j
        i += 1
        df.to_sql(table, db, if_exists="append")
        j = df.index[-1] + 1
    return


if __name__ == "__main__":
    if len(sys.argv) == 2:
        csv_file = sys.argv[1]
        db_file = sys.argv[2]
    else:
        csv_file = "fingerprint.delta.2019-01.csv"
        db_file = "work/csv_database.db"


#  into_database("work/fpmbid.csv", db_file, "fpmbid")
#  into_database("work/fingerprint.delta.2019-01.csv", db_file, "table")
#  into_database("work/mbid.2019.csv", db_file, "mbid")
