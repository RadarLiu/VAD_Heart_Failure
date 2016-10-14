#10.13: for parsing patients for SPADE (from heart problem to death)
def clean(item):
    ans = ''
    for c in item:
        #if (('0' <= c and c <= '9') or ('A' <= c and c <= 'Z') or ('a' <= c and c <= 'z')):
        if ('0' <= c and c <= '9'):
            ans += c
    return ans

def parse_time(s):  #approximate seconds from "2000-01-01 00:00:00"
    fields = s[1:20].split(' ')
    seconds = 0
    date = fields[0].split('-')
    seconds += (int(date[0]) - 2000) * 365 * 86400
    seconds += (int(date[1]) - 1) * 30 * 86400
    seconds += (int(date[2]) - 1) * 86400
    time = fields[1].split(':')
    seconds += int(time[0]) * 12 * 60
    seconds += int(time[1]) * 60
    seconds += int(time[2])
    return str(seconds)


#set for dead people
dead_set = set()
f0 = open('dead_patients.csv', 'r')
for line in f0:
    #print line + ' ' + str(len(line))
    dead_set.add(line[:len(line) - 2])
f0.close()

#for sid in dead_set:
#    print sid

f1 = open('fp_diagnose_in.csv', 'r')
f2 = open('spade_in_ready_diagnose_from_heart_to_death.csv', 'w')
cnt = 0
sid_old = -1
time_old = ""
item_list = []

#below are the min / max timestamp threshold (inclusive) 
#(mining on the entire sequence is too slow....)
min_line_tms = 1
max_line_tms = 5
tms = 0

trigger = False
for line in f1: # 3, "2101-10-20 19:59:00",50893  (sid, time, item(diagnose))
    cnt += 1
    if (cnt % 100000 == 0):
        print cnt
    fields = line.split(',')
    sid = fields[0]
    if (not (sid in dead_set)): continue  #filter away those hasn't died
    #print "breach"
    time = fields[1]
    item = fields[2]
    if ((sid_old == sid and time_old == time) or (sid_old == -1)):
        sid_old = sid
        time_old = time
        ss = clean(item)
        if (ss.startswith('428') and trigger == False):
            trigger = True
        if (len(ss) > 0 and trigger):
            item_list.append(ss)
    elif (sid_old == sid and time_old != time):  #another transaction in this person
        #dump segment
        tms += 1
        if (min_line_tms <= tms and tms <= max_line_tms):
            content = ''
            for it in item_list:
                content += it + ' '
            content += '-1 '  #end of transaction
            f2.write(content)
            time_old = time
            item_list = []
            ss = clean(item)
            if (ss.startswith('428') and trigger == False):
                trigger = True
            if (len(ss) > 0 and trigger):
                item_list.append(ss)
        else: continue
    elif (sid_old != sid):  #another person
        #dump segment & new line
        trigger = False
        if (min_line_tms <= tms and tms <= max_line_tms):
            content = ''
            for it in item_list:
                content += it + ' '
            if (len(content) > 0):
                content += '-1 999999999 -1 -2'  #end of transaction, 999999999 means death
                content += '\n'
                f2.write(content)
        else:
            pass
        time_old = time
        sid_old = sid
        item_list = []
        tms = 0
        ss = clean(item)
        if (ss.startswith('428') and trigger == False):
            trigger = True
        if (len(ss) > 0 and trigger):
            item_list.append(ss)
#dump last time
content = ''
for it in item_list:
    content += it + ' '
if (len(content) > 0):
    content += '-1'
    f2.write(content)
f1.close()
f2.close()
