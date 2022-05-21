# -*- coding: UTF-8 -*
import sys
import os

match_str = "match_num:0"
count = 0
def main():
    while True:
        try:
            try:
                global count
                line = sys.stdin.readline()
                if line == '' or line == '\n':
                    break
            except Exception as e:
                print >> sys.stderr, "[Line 15]:" + str(e) + "readline failed"

            if 'match_num:' in line:
                try:
                    current_count = int(line.strip().split(':')[1])
                    count = count + current_count
                except Exception as e:
                    print >> sys.stderr, "[Line 22]: " + str(e) + ":count compute error!"
        except Exception as e:
            print >> sys.stderr, "[Line 31]: " + str(e) + ":process data error!"

    print str("match_num:") + str(count)

if __name__ == '__main__':
    main()