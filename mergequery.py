import sqlite3


def getdb():
    conn = sqlite3.connect('spring22.db')
    cur = conn.cursor()
    cur.execute("""select tbl_name from sqlite_master where type = 'table' and name not like 'sqlite_%' 
    and name <> 'sections' and name <> 'names'""")
    depts = [x[0] for x in cur.fetchall()]
    lines = ["SELECT * FROM {}".format(x) for x in depts]
    for x in lines:
        print("WITH details(course_num, open_seats, total_seats, reserves, percentage, time_recorded) AS (" + x +
              ") SELECT details.course_num, dept, catalog_num, course_name, section_type, section_num, topic,"
              "open_seats, total_seats, reserves, time_recorded FROM details, sections, names "
              "WHERE names.course_num = details.course_num AND sections.course_num = details.course_num;")


if __name__ == '__main__':
    getdb()