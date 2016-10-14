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

diagnose_dict['999999999'] = 'DEATH'

#convert data
f1 = open('spade_in_ready_diagnose_from_heart_to_death.out', 'r')
f2 = open('spade_diagnose_from_heart_to_death(final).txt', 'w')
for line in f1:
    if not ('999999999' in line): continue
    #make sure that heart-related problems occur in the first set
    first_neg_one = line.index('-1')
    first_part = line[0:first_neg_one]
    if not ('428' in first_part):continue

    fields = line.split(' ')
    length = len(fields)
    content = ''
    if (length < 6):
        continue
    for i in range(0, length - 2):
        try:
            label = int(fields[i])
            if (label == -1):
                if (i < length - 3):
                    content += '-> '
            else:
                content += ('\"' + diagnose_dict[str(label)] + '\" ')
        except: pass
    content += (fields[length - 2] + ' ' + fields[length - 1])
    if ('->' in content):
        f2.write(content)
f1.close()
f2.close()
