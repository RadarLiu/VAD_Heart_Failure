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
f1 = open('fp_out_diagnose_sametime.txt', 'r')
f2 = open('fp_diag_same_time.txt', 'w')
for line in f1:
    fields = line.split(' ')
    length = len(fields)
    if (length < 4):
        continue
    for i in range(0, length - 2):
        try:
            f2.write('\"' + diagnose_dict[str(int(fields[i]))] + '\" ')
        except: pass
    f2.write(fields[length - 2] + ' ' + fields[length - 1])
f1.close()
f2.close()
