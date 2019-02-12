#!/usr/bin/env python3

import sys
import json
import sqlite3

DAT_FILE = "./scorelib.dat"


def get_prints_from_db(sql_database, cursor, searching_pattern):
    cursor.execute("SELECT print.id, print.partiture, person.name "
              "FROM print JOIN edition ON print.edition = edition.id "
              "JOIN score_author ON edition.score = score_author.score "
              "JOIN person ON score_author.composer = person.id WHERE person.name LIKE ?", (searching_pattern,))
    db_rows = cursor.fetchall()
    sql_database.commit()
    return db_rows


def get_composers_from_db(sql_database, cursor, id_print):
    cursor.execute("SELECT person.name, person.born, person.died "
              "FROM print JOIN edition ON print.edition = edition.id "
              "JOIN score_author ON edition.score = score_author.score "
              "JOIN person ON person.id = score_author.composer "
              "WHERE print.id=?", (id_print,))
    db_rows = cursor.fetchall()
    sql_database.commit()
    return db_rows


def get_editors_from_db(sql_database, cursor, id_print):
    cursor.execute("SELECT person.name, person.born, person.died "
              "FROM print JOIN edition_author ON print.edition = edition_author.edition "
              "JOIN person ON person.id = edition_author.editor "
              "WHERE print.id=?", (id_print,))
    db_rows = cursor.fetchall()
    sql_database.commit()
    return db_rows


def get_edition_from_db(sql_database, cursor, id_print):
    cursor.execute("SELECT edition.name, edition.year "
              "FROM print JOIN edition ON print.edition = edition.id "
              "WHERE print.id=?", (id_print,))
    db_rows = cursor.fetchone()
    sql_database.commit()
    return db_rows


def get_score_from_db(sql_database, cursor, id_print):
    cursor.execute("SELECT score.id, score.name, score.genre, score.key, score.incipit, score.year "
              "FROM print JOIN edition ON print.edition = edition.id "
              "JOIN score ON score.id = edition.score "
              "WHERE print.id=?", (id_print,))
    db_row = cursor.fetchone()
    sql_database.commit()
    return db_row


def get_voices_from_db(sql_database, cursor, id_score):
    cursor.execute("SELECT voice.number, voice.range, voice.name "
              "FROM voice JOIN score ON score.id = voice.score "
              "WHERE score.id=?", (id_score,))
    db_rows = cursor.fetchall()
    sql_database.commit()
    return db_rows


def main():
    name_to_search = sys.argv[1]
    sql_database = sqlite3.connect(DAT_FILE)
    cursor = sql_database.cursor()

    searching_pattern = "%" + name_to_search + "%"
    prints = get_prints_from_db(sql_database, cursor, searching_pattern)

    all_info = {}
    for one_print in prints:
        all_info[one_print[2]] = []

    for one_print in prints:
        composers = get_composers_from_db(sql_database, cursor, one_print[0])
        editors = get_editors_from_db(sql_database, cursor, one_print[0])
        score = get_score_from_db(sql_database, cursor, one_print[0])
        edition = get_edition_from_db(sql_database, cursor, one_print[0])
        voices = (get_voices_from_db(sql_database, cursor, score[0]))

        print_dict = {}
        print_dict["Print Number"] = one_print[0]
        print_dict["Composer"] = [{"Name": composer[0], "Born": composer[1], "Died": composer[2]} for composer in composers]
        print_dict["Title"] = score[1]
        print_dict["Genre"] = score[2]
        print_dict["Key"] = score[3]
        print_dict["Composition Year"] = score[5]
        print_dict["Publication Year"] = edition[1]
        print_dict["Edition"] = edition[0]
        print_dict["Editor"] = [{"Name": editor[0], "Born": editor[1], "Died": editor[2]} for editor in editors]
        print_dict["Voices"] = {voice[0]: {"Range": voice[1], "Name": voice[2]} for voice in voices}
        print_dict["Partiture"] = True if one_print[1] == 'Y' else False
        print_dict["Incipit"] = score[4]

        all_info[one_print[2]].append(print_dict)

    print(json.dumps(all_info, ensure_ascii=False, indent=2))
    sql_database.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("argv error: not enough program arguments")
        print("invocation: ./search.py composer_substring")
        sys.exit()

    main()


