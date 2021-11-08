import sqlite3


def getdb():
    conn = sqlite3.connect('spring22.db')
    cur = conn.cursor()
    cur.execute("""select tbl_name from sqlite_master where type = 'table' and name not like 'sqlite_%' 
    and name <> 'sections' and name <> 'names'""")
    depts = [x[0] for x in cur.fetchall()]
    lines = ["SELECT * FROM {}".format(x) for x in depts]
    print(".headers on\n.mode csv")
    for x in lines:
        name = x[x.find("FROM") + 5:]
        print(".output " + name + ".csv")
        print("WITH details(course_num, open_seats, total_seats, reserves, percentage, time_recorded) AS (" + x +
              ") SELECT details.course_num, dept, catalog_num, course_name, topic, section_type, section_num,"
              "open_seats, total_seats, reserves, percentage, time_recorded FROM details, sections, names "
              "WHERE names.course_num = details.course_num AND sections.course_num = details.course_num"
              " AND dept = '" + name + "';")


if __name__ == '__main__':
    getdb()