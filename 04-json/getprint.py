#!/usr/bin/env python3

import sys
import json
import sqlite3

DAT_FILE = "./scorelib.dat"

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("argv error: not enough program arguments")
        print("invocation: ./getprint.py print_number")
        sys.exit()

    print_id = sys.argv[1]
    sql_database = sqlite3.connect(DAT_FILE)
    c = sql_database.cursor()

    c.execute("SELECT person.name, person.born, person.died "
              "FROM print JOIN edition ON print.edition = edition.id "
              "JOIN score_author ON edition.score = score_author.score "
              "JOIN person ON person.id = score_author.composer WHERE print.id = ?", (print_id, ))


    composers = []
    rows = c.fetchall()
    for row in rows:
        composer = {"name": row[0]}
        if row[1]:
            composer["born"] = row[1]
        if row[2]:
            composer["died"] = row[2]

        composers.append(composer)

    print(json.dumps(composers, ensure_ascii=False, indent=2))
    sql_database.close()
