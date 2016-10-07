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
#convert data
f1 = open('spade_out_diagnose.txt', 'r')
f2 = open('spade_diagnose(final).txt', 'w')
for line in f1:
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
