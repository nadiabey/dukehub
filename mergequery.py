import sqlite3


def getdb():
    conn = sqlite3.connect('testrun.db')
    cur = conn.cursor()
    cur.execute("""select tbl_name from sqlite_master where type = 'table' and name not like 'sqlite_%' 
    and name <> 'sections' and name <> 'names'""")
    depts = [x[0] for x in cur.fetchall()]
    lines = ["SELECT * FROM {}".format(x) for x in depts]
    ret = ""
    for x in lines:
        if x is not lines[-1]:
            ret += x
            ret += " UNION ALL "
        else:
            ret += x
    return ret

if __name__ == '__main__':
    string = getdb()
    ret = "WITH classdetails(course_num, course_name, topic, dept, catalog_num) AS (" + string + \
          ") SELECT course_num, dept, catalog_num, course_name, section_type, section_num," \
          "open_seats, total_seats, reserves, time_recorded FROM classdetails, sections, names"
    print(ret)