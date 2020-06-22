import curses
import urllib.request, json 
import datetime
import os.path

max_day = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

bob_data = {}
eng2kor = {'breakfast': '아침', 'lunch': '점심', 'dinner': '저녁'}

def init():
    if not os.path.isfile('./bob.db'):
        f = open('./bob.db', 'w')
        f.close()

def fetch_bob(month):
    with open('./bob.db', 'r') as f:
        for tmp in f.readlines():
            date = int(tmp.split('%')[0])
            meal = {
                'breakfast': tmp.split('%')[1],
                'lunch': tmp.split('%')[2],
                'dinner': tmp.split('%')[3].replace('\n', ''),
            }
            # print(date, meal)
            bob_data[date] = meal
    for i in range(20200000 + month * 100 + 1, 20200000 + month * 100+ max_day[month] + 1):
        if i not in bob_data:
            # print("https://api.dimigo.in/dimibobs/" + str(i) + '/')
            try:
                with urllib.request.urlopen("https://api.dimigo.in/dimibobs/" + str(i) + '/') as url:
                    bob_data[i] = json.loads(url.read().decode())
                    # print("fetch %d:" % i, bob_data[i])
            except:
                # print('failed to fetch %d' % i)
                break
    # print(bob_data)
    with open('./bob.db', 'w') as f:
        for i in bob_data:
            f.write("%d%%%s%%%s%%%s\n" % (i, bob_data[i]['breakfast'], \
                            bob_data[i]['lunch'], bob_data[i]['dinner']))


def bob_time(ban, date):
    time = {
        'lunch': [47400, 47580, 47760, 47940, 48120, 48300],
        'dinner': [69300, 69480, 69660, 69840, 70020, 70200]
    }
    
    w = date.isocalendar()[1]
    d = date.isocalendar()[2]

    # print('w', w, 'd', d)

    p = 0
    if w < 35:
        p = w - 22
        if d < 3:
            p -= 1
    else:
        p = w - 33
    p = p % 6
    # print('p', p)

    return (datetime.timedelta(seconds=time['lunch'][(ban - p) % 6]),
            datetime.timedelta(seconds=time['dinner'][5 - (ban - p) % 6]))


def display_bob(stdscr, date):
    # print(date, type(date))

    stdscr.addstr(0, 0, "Press ';' for help. (WIP)", curses.color_pair(3))
    stdscr.addstr(1, 0, "Press 'q' to quit.", curses.color_pair(3))

    date_str = date.year * 10000 + date.month * 100 + date.day
    stdscr.addstr(1, 30, '{}년 {:0>2}월 {:0>2}일'.format(date.year, date.month, date.day))
    
    for i in range(3, 20):
        stdscr.addstr(i, 0, ' ' * 100)
    if date_str in bob_data:
        col = -24
        for k in eng2kor:
            line = 3
            col += 25
            stdscr.addstr(line, col, eng2kor[k] + ' ', curses.color_pair(1))
            time = bob_time(6, date)
            if k == 'lunch':
                stdscr.addstr(line, col + 5, str(time[0]), curses.color_pair(1))
            elif k == 'dinner':
                stdscr.addstr(line, col + 5, str(time[1]), curses.color_pair(1))
            for j in bob_data[date_str][k].split('/'):
                line += 1
                if line < 40:
                    stdscr.addstr(line, col + 1, j + '\n')
    else:
        stdscr.addstr(4, 28, '급식 정보가 없습니다')
    stdscr.move(0, 0)
    stdscr.refresh()
        

def main(stdscr):
    stdscr.clear()

    now = datetime.datetime.now()

    curses.init_pair(1, 184, 0)
    curses.init_pair(2, 123, 0)
    curses.init_pair(3, 248, 0)

    display_bob(stdscr, now)
    while True:
        key = stdscr.getkey() 
        if key == 'q':
            break
        if key == 'l':
            now = (now + datetime.timedelta(seconds=86400))
            display_bob(stdscr, now)
        if key == 'h':
            now = (now - datetime.timedelta(seconds=86400))
            display_bob(stdscr, now)


init()
fetch_bob(6)
curses.wrapper(main)
bob_time(1, datetime.datetime(2020, 6, 3, 00,0,0))