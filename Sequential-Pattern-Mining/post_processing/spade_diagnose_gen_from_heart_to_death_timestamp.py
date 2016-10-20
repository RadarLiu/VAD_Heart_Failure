#create diagnose dict
fd = open('D_ICD_DIAGNOSES.csv', 'r')
diagnose_dict = {}
for line in fd:
    fields = line.split(',')
    icd9 = fields[1]
    try:
        icd9 = str(int(icd9[1 : len(icd9) - 1]))
        short_title = fields[2]
        short_title = short_title[1 : len(short_title) - 1]
        diagnose_dict[icd9] = short_title
    except: pass
fd.close()

diagnose_dict['9999'] = 'DEATH'

#convert data
f1 = open('spade_in_ready_diagnose_from_heart_to_death_timestamp_revised.out', 'r')
f2 = open('spade_diagnose_from_heart_to_death_final_revised.txt', 'w')
timestamp = ''
for line in f1:
    if not ('989999' in line): continue   #must contain death!
    #make sure that heart-related problems occur in the first set
    first_neg_one = line.index('-1')
    first_part = line[0:first_neg_one]
    if not ('428' in first_part):continue

    fields = line.split(' ')   #line: a single line with multiple transactions!
    length = len(fields)
    content = ''
    if (length < 6):
        continue
    for i in range(0, length - 2):
        try:
            label = int(fields[i])  #timestamp98label
            if (label == -1):
                content += '[' + timestamp + '] '
                if (i < length - 3):
                    content += '-> '
            else:
                #extract timestamp from "9timestamp9" in the beginning of every item in this transaction
                label_s = str(label)
                delim_idx = label_s.index('98')
                timestamp = label_s[0:delim_idx]
                timestamp = str(int(timestamp) - 1) #there is a "1 offset in pre-porcessing"
                #print timestamp
                diagnose_name = label_s[delim_idx + 2 : len(label_s)]
                #print diagnose_name
                content += ('\"' + diagnose_dict[str(diagnose_name)] + '\" ')
        except: pass
    content += (fields[length - 2] + ' ' + fields[length - 1])
    if ('->' in content):
        f2.write(content)
f1.close()
f2.close()
