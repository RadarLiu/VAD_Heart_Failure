#11.6: removed "from heart problem to death" filter
def clean(item):
    ans = ''
    for c in item:
        #if (('0' <= c and c <= '9') or ('A' <= c and c <= 'Z') or ('a' <= c and c <= 'z')):
        if ('0' <= c and c <= '9'):
            ans += c
    return ans

def parse_time(s):  #approximate seconds from "2000-01-01 00:00:00"
    try:
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
    except:
        print s
    #return str(seconds)
    return seconds

def get_months_by_seconds(sec):
    return sec / 30 / 86400 / 3;  #bin: 3 months

def get_year_by_seconds(sec):
    return sec / 86400 / 365;

def age_bin(age):  #convert an age to a bin number: under 25, 25 - 30, 30+
    if (age < 25):
        return '0'
    elif (age <= 30):
        return '1'
    else:
        return '2'

#map people to date of death
dead_map = {}
f0 = open('dead_patients_with_time.csv', 'r')
for line in f0:
    #print line + ' ' + str(len(line))
    fields = line.split(',')
    dead_map[fields[0]] = (fields[1][:len(fields[1]) - 2]) #to get rid of double quote
f0.close()

birth_map = {}
printed_dob = {}
#f0 = open('dead_patients_with_dob.csv', 'r')
f0 = open('all_patients_with_dob.csv', 'r')
for line in f0:
    fields = line.split(',')
    birth_map[fields[0]] = (fields[1][:len(fields[1]) - 2])
    printed_dob[fields[0]] = False
f0.close()


#for sid in dead_set:
#    print sid

f1 = open('fp_diagnose_in.csv', 'r')
f2 = open('spade_in_ready_diagnose_timestamp_revised_with_dob.csv', 'w')
cnt = 0
sid_old = -1
time_old = ""
time_start = "" #"start record" time for a single patient. 
#Note that we need to use timestamp (rather than time interval) because SPADE
#may "skip" part of one sequence
item_list = []

#below are the min / max timestamp threshold (inclusive) 
#(mining on the entire sequence is too slow....)
min_line_tms = 1
max_line_tms = 5
tms = 0

trigger = False
timestamp = 0  #timestamp at the granularity of month (30 days)
for line in f1: # 3, "2101-10-20 19:59:00",50893  (sid, time, item(diagnose))
    cnt += 1
    if (cnt % 100000 == 0):
        print cnt
    fields = line.split(',')
    sid = fields[0]
    #if (not (sid in birth_map)): continue
    #print "breach"
    time = fields[1]
    item = fields[2]
    if ((sid_old == sid and time_old == time) or (sid_old == -1)):
        sid_old = sid
        time_old = time
        if (sid_old == -1):
            time_start = time
        ss = clean(item)
        #if (ss.startswith('428') and trigger == False):
        trigger = True
        timestamp = 0
        if (len(ss) > 0 and trigger):
            item_list.append(ss)
    elif (sid_old == sid and time_old != time):  #another transaction (time) in this person
        #dump segment
        tms += 1
        if (min_line_tms <= tms and tms <= max_line_tms):
            content = ''
            if (not printed_dob[sid_old]):
                age_of_first_record = get_year_by_seconds(parse_time(time_start) - parse_time(birth_map[sid_old]))
                content = age_bin(age_of_first_record) + ' -1 '  #start with age
                printed_dob[sid_old] = True
            #content = ''
            #IMPORTANT! IMPORTANT! IMPORTANT! "+1" is to avoid "098..." be regarded as "98..." by spade!
            #Need to -1 in post processing! 
            time_interval = str(get_months_by_seconds(parse_time(time_old) - parse_time(time_start)) + 1)
            for it in item_list:
                content += '' + time_interval + '98' + it + ' '
            #content += '[' + str(get_months_by_seconds(parse_time(time) - parse_time(time_old))) + '] '
            #content += str(get_months_by_seconds(parse_time(time) - parse_time(time_old)))
            content += '-1 '  #end of transaction
            f2.write(content)
            time_old = time
            item_list = []
            ss = clean(item)
            #if (ss.startswith('428') and trigger == False):
            #    trigger = True
            #    timestamp = 0
            trigger = True
            timestamp = 0
            if (len(ss) > 0 and trigger):
                item_list.append(ss)
        else: continue
    elif (sid_old != sid):  #another person
        #dump segment & new line
        trigger = False
        timestamp = 0
        if (min_line_tms <= tms and tms <= max_line_tms):
            content = ''
            #IMPORTANT! IMPORTANT! IMPORTANT! "+1" is to avoid "098..." be regarded as "98..." by spade!
            #Need to -1 in post processing! 
            time_interval = str(get_months_by_seconds(parse_time(time_old) - parse_time(time_start)) + 1)
            for it in item_list:
                content += '' + time_interval + '98' + it + ' '
            if (sid_old in dead_map):
                time_interval = str(get_months_by_seconds(parse_time(dead_map[sid_old]) - parse_time(time_start)) + 1)
                if (len(content) > 0):
                    #content += str(get_months_by_seconds(parse_time(dead_map[sid_old]) - parse_time(time_old)))
                    content += '-1 ' + time_interval + '989999 -1 -2'  #end of transaction, 9999 means death, 98 is deliminator
                    content += '\n'
                    #age_of_first_record = get_year_by_seconds(parse_time(time_start) - parse_time(birth_map[sid_old]))
                    #content = str(age_of_first_record) + ' -1 ' + content
                    f2.write(content)
            else:
                if (len(content) > 0):
                    content += '-1 -2\n'
                    f2.write(content)
        else:
            pass
        time_old = time
        sid_old = sid
        time_start = time
        item_list = []
        tms = 0
        ss = clean(item)
        #if (ss.startswith('428') and trigger == False):
        #    trigger = True
        #    timestamp = 0
        trigger = True
        timestamp = 0
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
