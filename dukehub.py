import datetime, time, multiprocessing, sqlite3
from sqlite3 import Error
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
driver = webdriver.Chrome(r"/Users/nadiabey/Documents/Duke/Chronicle/dukehub/chromedriver", options=chrome_options)
conn = sqlite3.connect("spring22.db")
driver.implicitly_wait(10)


def init():
    """
    open dukehub landing page and navigate to public class search
    """
    driver.get(
        "https://dukehub.duke.edu/psc/CSPRD01/EMPLOYEE/SA/s/WEBLIB_HCX_GN.H_SPRINGBOARD.FieldFormula.IScript_Main"
        "?&institution=DUKEU")
    catalog = driver.find_element_by_xpath("/html/body/div/main/div/div/div[4]/div/button")
    catalog.click()
    iframe = driver.find_element_by_xpath("/html/body/div[1]/iframe")
    driver.switch_to.frame(iframe)


def get_term(x: str):
    """
    input given term (Fall 2021, etc)
    """
    term = driver.find_element_by_xpath("/html/body/div[1]/main/div/form/div/div[2]/div/div/div/input")
    term.clear()
    term.send_keys(x)
    term.send_keys(Keys.ARROW_DOWN)
    term.send_keys(Keys.RETURN)
    time.sleep(4)


def get_career(x: str):
    """
    input given career x (undergraduate, graduate, etc)
    """
    career = driver.find_element_by_xpath("/html/body/div[1]/main/div/form/div/div[3]/div/div/div/input")
    career.clear()
    career.send_keys(x)
    career.send_keys(Keys.ARROW_DOWN)
    career.send_keys(Keys.RETURN)


def show_all():
    """
    uncheck 'open classes only'
    """
    closed = driver.find_element_by_xpath("/html/body/div[1]/main/div/form/div/div[22]/label/span[1]/span[1]/input")
    closed.click()


def start(term: str, career: str):
    init()
    get_term(term)
    get_career(career)
    show_all()


def search_button():
    """
    click search
    """
    search = driver.find_element_by_xpath("/html/body/div[1]/main/div/form/div/div[20]/button")
    search.click()


def page_end():
    """
    scroll to bottom of page to load all classes
    """
    try:
        driver.find_element_by_xpath("/html/body/div[1]/main/div/p/div/div[2]/span")
    except NoSuchElementException:
        ActionChains(driver).send_keys(Keys.END).perform()
        time.sleep(4)
        page_end()
    finally:
        time.sleep(3)


def depttable(dept: str):
    table = """CREATE TABLE IF NOT EXISTS {} (
    course_num INTEGER NOT NULL,
    open_seats INTEGER NOT NULL,
    total_seats INTEGER NOT NULL,
    reserves TEXT NOT NULL,
    percentage REAL NOT NULL,
    time_recorded TEXT NOT NULL,
    PRIMARY KEY (course_num, time_recorded))""".format(dept)
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute(table)
        except Error as e:
            print(e)
    else:
        print("Error - cannot make connection")


def deptinsert(dept: str, vals: tuple):
    add = """ INSERT OR IGNORE INTO {} values(?,?,?,?,?,?)""".format(dept)
    cur = conn.cursor()
    cur.execute(add, vals)
    conn.commit()
    return cur.lastrowid


def sectioninsert(vals: tuple):
    """
    insert section details into table
    """
    add = """INSERT OR IGNORE INTO sections values(?,?,?)"""
    cur = conn.cursor()
    cur.execute(add, vals)
    conn.commit()
    return cur.lastrowid


def nameinsert(vals: tuple):
    """
    add tuples containing names of classes to database
    """
    add = "INSERT OR IGNORE INTO names values(?,?,?,?,?)"
    cur = conn.cursor()
    cur.execute(add, vals)
    conn.commit()
    return cur.lastrowid


def num_search(y: list):
    """
    get all class details by department; y contains extracted html
    """
    temp = []
    for item in y:
        if "Class Number" in item:
            index = item.rfind('r')
            num = item[index + 1:]
            section = item[0:item.find(',')]
            sec_typ = section.split(" Section ")[0]
            sec_num = section.split(" Section ")[1]
            sectioninsert((num, sec_typ, sec_num))
            temp.append(num) # index 0 - course number

        if "seats" in item:
            # reserved and waitlist use rfind because 'seats' is present multiple times
            if "reserved" in item:
                if "Closed" not in item:
                    avail = int(item[item.find('d,') + 3:item.find('of') - 1])
                    total = int(item[item.find('of') + 3:item.rfind('seats') - 1])
                    temp.append(avail) # index 1 - open seats
                    temp.append(total) # index 2 - total seats
                else:
                    avail = int(item[item.rfind('d,') + 3:item.find('of') - 1])
                    total = int(item[item.find('of') + 3:item.rfind('seats') - 1])
                    temp.append(avail)
                    temp.append(total)
                temp.append("Yes") # index 3 - reserves
            elif "waitlist" in item:
                avail = int(item[item.find('e.') + 3:item.rfind('of') - 1])
                total = int(item[item.rfind('of') + 3:item.rfind('seats') - 1])
                temp.append(avail) # index 1
                temp.append(total) # index 2
                temp.append("No") # index 3
            else:
                avail = int(item[item.find(',') + 2:item.find('of') - 1])
                total = int(item[item.find('of') + 3:item.find('seats') - 1])
                temp.append(avail) # index 1
                temp.append(total) # index 2
                temp.append("No") # index 3
            try:
                percent = ((total - avail) / total * 100) # index 4
                temp.append(percent)
            except ZeroDivisionError:
                percent = 9999
                temp.append(percent)
            finally:
                temp.append(str(datetime.datetime.now())) # index 5
    return temp


def department(dept):
    try:
        name = dept[0:dept.index("-") - 1]
    except ValueError:   # for strings without hyphens keep same one (i.e. mech engineering)
        name = dept
    if "&" in name:
        name = name.replace("&","")  # remove extra symbol to avoid sql syntax error
    subject = driver.find_element_by_xpath("/html/body/div[1]/main/div/form/div/div[4]/div/div/div/input")
    subject.clear()
    subject.send_keys(dept)
    subject.send_keys(Keys.ARROW_DOWN)
    subject.send_keys(Keys.RETURN)
    search_button()
    print(name, "started at", str(datetime.datetime.now()))
    begin = time.time()
    page_end()
    data = [x.text for x in driver.find_elements_by_xpath("//span[contains(@class, 'sr-only')]")]
    classes = num_search(data)
    values = []  # holds tuples for each course
    for y in [classes[x:x+6] for x in range(0, len(classes), 6)]:
        values.append((y[0], y[1], y[2], y[3], y[4], y[5]))
    depttable(name)
    for x in values:
        deptinsert(name, x)
    end = time.time()
    print(name, end - begin)


def get_class(x: str):
    """
    search for class number and return name
    """
    classNumber = driver.find_element_by_xpath("/html/body/div[1]/main/div/form/div/div[7]/div/div/div/input")
    classNumber.clear()
    classNumber.send_keys(x)
    search = driver.find_element_by_xpath("/html/body/div[1]/main/div/form/div/div[20]/button")
    search.click()
    time.sleep(4)
    details = [x.text for x in
               driver.find_elements_by_xpath("//div[contains(@class, 'MuiGrid-root MuiGrid-container')]")]
    cn = driver.find_element_by_xpath("/html/body/div[1]/main/div/form/div/div[7]/div/div/div/input")
    # cn is new version of classNumber because page changed
    for i in range(len(str(x))):
        cn.send_keys(Keys.BACKSPACE)
    try:
        findtopic = details[1].split("\n")
        topic = findtopic[14]
        nt = findtopic[0].split(" | ")
        className = nt[0]
        dept = nt[1].split(" ")[0]
        if "&" in dept:
            dept = dept.replace("&", "")
        catnum = nt[1].split(" ")[1]
        course = (x, className, topic, dept, catnum)
        nameinsert(course)
    except IndexError:
        course = (x, "not found", "NA", "NA", "NA")
        nameinsert(course)


def run_search(term, career, dept):
    start(term, career)
    department(dept)


def run_indiv(term, career, num):
    print(num)
    start(term, career)
    get_class(num)


def get_names(term, career):
    cur = conn.cursor()
    cur.execute("""SELECT course_num from sections""")
    nums = [x[0] for x in cur.fetchall()]
    cur.execute("""SELECT course_num from names""")
    exclude = [x[0] for x in cur.fetchall()]
    queries = [x for x in nums if x not in exclude]
    print('start time: ', str(datetime.datetime.now()))
    first = time.time()
    pool = multiprocessing.Pool()
    pool.starmap(run_indiv, [(term, career, x) for x in queries])
    pool.close()
    driver.quit()
    last = time.time()
    print('end time: ', str(datetime.datetime.now()))
    print('time elapsed: ', last - first, 'seconds')


def get_data(term: str, career: str, x: list):
    print('start time: ', str(datetime.datetime.now()))
    first = time.time()
    pool = multiprocessing.Pool()
    pool.starmap(run_search, [(term, career, dept) for dept in x])
    pool.close()
    driver.quit()
    last = time.time()
    print('end time: ', str(datetime.datetime.now()))
    print('time elapsed: ', last - first, 'seconds')


if __name__ == '__main__':
    testy = ['AAAS -', 'BIOLOGY -', 'VMS -']
    listy = [x[:-1] for x in open('spring22.txt', 'r').readlines()]
    prompt = input("Which code is being initiated? ")
    when = input("What term: ")
    who = input("What career: ")
    if prompt == "data":
        month = datetime.datetime.today().month
        day = datetime.datetime.today().day
        while datetime.datetime.now() < datetime.datetime(2021, month, day, 17, 10):
            get_data(when, who, listy)
            if datetime.datetime.now() > datetime.datetime(2021, month, day, 17, 10):
                break
    if prompt == "names":
        get_names(when, who)
    conn.close()
