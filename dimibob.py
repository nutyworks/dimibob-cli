import curses
import urllib.request, json 
from colored import fg, bg, attr
from datetime import datetime

max_day = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

bob_data = {}
eng2kor = {'breakfast': '아침', 'lunch': '점심', 'dinner': '저녁'}

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
                print('failed to fetch %d' % i)
                break
    # print(bob_data)
    with open('./bob.db', 'w') as f:
        for i in bob_data:
            f.write("%d%%%s%%%s%%%s\n" % (i, bob_data[i]['breakfast'], \
                            bob_data[i]['lunch'], bob_data[i]['dinner']))
        

def main(stdscr):
    stdscr.clear()
    now = datetime.now()
    now_str = now.year * 10000 + now.month * 100 + now.day
    # keymap = # q: quit, l: next day, h: prev day    
    print(now_str)
    # print(bob_data[now_str])
    # input()
    curses.init_pair(1, 184, 0)
    curses.init_pair(2, 123, 0)
    line = 0
    col = -24
    for k in eng2kor:
        line = 1
        col += 25
        stdscr.addstr(line, col, eng2kor[k] + ' ', curses.color_pair(1))
        for j in bob_data[now_str][k].split('/'):
            line += 1
            if line < 40:
                stdscr.addstr(line, col + 1, j + '\n')
            # stdscr.addstr('\n')
            # stdscr.addstr(j + '\n', curses.color_pair(2))
        # stdscr.addstr(sp_meal + '\n', curses.color_pair(2))
        
    stdscr.refresh()
    stdscr.getkey()

fetch_bob(6)
# print(bob_data)
curses.wrapper(main)