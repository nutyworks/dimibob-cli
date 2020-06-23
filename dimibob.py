import curses
import urllib.request, json 
import datetime
import os.path

max_day = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

bob_data = {}
raw_data = {}
eng2kor = {'breakfast': '아침', 'lunch': '점심', 'dinner': '저녁'}

def init():
    if not os.path.isfile('/tmp/bob.db'):
        f = open('/tmp/bob.db', 'w')
        f.close()

def fetch_bob(month):
    with open('/tmp/bob.db', 'r') as f:
        for tmp in f.readlines():
            date = int(tmp.split('%')[0])
            meal = {
                'breakfast': tmp.split('%')[1],
                'lunch': tmp.split('%')[2],
                'dinner': tmp.split('%')[3].replace('\n', ''),
            }
            # print(date, meal
            raw_data[date] = tmp.split('%', 1)[1]
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
    with open('/tmp/bob.db', 'w') as f:
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

    lunch_time = time['lunch'][(ban - p) % 6]
    dinner_time = time['dinner'][5 - (ban - p) % 6]
    if d == 3:
        dinner_time -= 1500

    return (datetime.timedelta(seconds=lunch_time),
            datetime.timedelta(seconds=dinner_time))


def display_bob(stdscr, date):
    # print(date, type(date))

    stdscr.addstr(0, 0, "Press ';' for help.", curses.color_pair(3))
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


def display_help(stdscr):
    stdscr.clear()

    stdscr.addstr(0, 0, "Press ';' for bob.", curses.color_pair(3))
    stdscr.addstr(1, 0, "Press 'q' to quit.", curses.color_pair(3))

    stdscr.addstr(3, 1, "H - 1주 전으로 이동")
    stdscr.addstr(4, 1, "h - 1일 전으로 이동")

    stdscr.addstr(6, 1, "L - 1주 후로 이동")
    stdscr.addstr(7, 1, "l - 1일 후로 이동")

    stdscr.addstr(9, 1, "t - 오늘로 이동")
        

def main(stdscr):
    stdscr.clear()

    now = datetime.datetime.now()

    curses.init_pair(1, 184, 0)
    curses.init_pair(2, 123, 0)
    curses.init_pair(3, 248, 0)

    display_bob(stdscr, now)
    
    is_help_screen = False
    is_searching = False

    cursor = 8

    while True:
        key = stdscr.getkey() 
        if is_help_screen:
            if key == ';':
                is_help_screen = not is_help_screen
                display_bob(stdscr, now)
        elif is_searching:
            if key == '\n':
                is_searching = False
                curses.noecho()
            elif ord(key[0]) == 27:
                is_searching = False
                curses.noecho()
            elif key == 'KEY_BACKSPACE':
                s = stdscr.getstr(2, cursor - 2, 1)

                if ord(s) < 128:
                    cursor -= 1
                    if cursor < 8:
                        cursor = 8
                    stdscr.addstr(2, cursor, " ")
                else:
                    cursor -= 2
                    if cursor < 8:
                        cursor = 8
                    stdscr.addstr(2, cursor, "  ")

                stdscr.move(2, cursor)
            else:
                if ord(key[0]) < 200:
                    cursor += 1
                print(cursor, ord(key))

        elif key == 'q':
            break
        else:
            if key == 't':
                now = datetime.datetime.now()
                display_bob(stdscr, now)
            elif key == 'l':
                now = (now + datetime.timedelta(seconds=86400))
                display_bob(stdscr, now)
            elif key == 'h':
                now = (now - datetime.timedelta(seconds=86400))
                display_bob(stdscr, now)
            elif key == 'L':
                now = (now + datetime.timedelta(seconds=604800))
                display_bob(stdscr, now)
            elif key == 'H':
                now = (now - datetime.timedelta(seconds=604800))
                display_bob(stdscr, now)
            elif key == '/':
                is_searching = True
                curses.echo()
                stdscr.addstr(2, 0, "Search: ")
            elif key == ';':
                is_help_screen = not is_help_screen
                display_help(stdscr)


init()
fetch_bob(6)
curses.wrapper(main)