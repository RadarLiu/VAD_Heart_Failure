import sys
from parser import to_diagnose_text, to_procedure_text, to_age, to_bmi

'''l = open('D_ICD_DIAGNOSES.csv')
lines = l.readlines()[1:]
lines = [line.split(',') for line in lines]
l.close()
icd9text = {line[1][1:-1]: line[2][1:-1] for line in lines}
l = open('D_ICD_PROCEDURES.csv')
lines = l.readlines()[1:]
lines = [line.split(',') for line in lines]
l.close()
icd9text['""'] = '""'

procedures_text['""'] = '""'
procedures_text = {line[1][1:-1]: line[2][1:-1] for line in lines}'''

f = open('diagnoses_hf.csv')
diagnoses = f.readlines()[1:]
f.close()
diagnoses = [line.strip().split(',') for line in diagnoses]

f = open('procedures_hf.csv')
procedures = f.readlines()[1:]
f.close()
procedures = [line.strip().split(',') for line in procedures]

icd9s = {}
i = 0
for line in diagnoses:
    diagnose = to_diagnose_text(line[4])
    #diagnose = line[4]
    if diagnose not in icd9s:
        icd9s[diagnose] = 0
    icd9s[diagnose] += 1
icd9s['Congestive heart failure; nonhypertensive'] = 0
procedures_icd9s = {}
for line in procedures:
    procedure = to_procedure_text(line[4])
    #procedure = line[4]
    if procedure not in procedures_icd9s:
        procedures_icd9s[procedure] = 0
    procedures_icd9s[procedure] += 1


admissions = {}
for line in diagnoses:
    if line[2] not in admissions:
        admissions[line[2]] = (line[1], [], [])
    admissions[line[2]][1].append(to_diagnose_text(line[4]))
print len(admissions)
for line in procedures:
    if line[2] not in admissions:
        continue
    admissions[line[2]][2].append(to_procedure_text(line[4]))

patients = {}
for admission in admissions.keys():
    admission_this = admissions[admission]
    most_frequent_diagnose = max(admission_this[1], key=lambda d: icd9s[d])
    most_frequent_procedure = ""
    if len(admission_this[2]) > 0:
        most_frequent_procedure = max(admission_this[2],
                                      key=lambda p: procedures_icd9s[p])
    '''
    diagnose_text = ""
    if most_frequent_diagnose in icd9text:
        diagnose_text = icd9text[most_frequent_diagnose]
    procedure_text = ""
    if most_frequent_procedure in procedures_text:
        procedure_text = procedures_text[most_frequent_procedure]
    # the_pair = (most_frequent_diagnose, most_frequent_procedure)
    the_pair = (diagnose_text, procedure_text)
    '''
    the_pair = (to_diagnose_text(most_frequent_diagnose),
                to_procedure_text(most_frequent_procedure))
    # admissions[admission] = [admission_this[0], diagnoses_pairs]
    if admissions[admission][0] not in patients:
        patients[admissions[admission][0]] = []
    patients[admissions[admission][0]].append((admission, the_pair))

print len(patients)
f = open('admissions.csv')
lines = f.readlines()[1:]
f.close()

lines = [line.strip().split(',') for line in lines]
times = {}
for line in lines:
    times[line[2]] = line[3]

for patient in patients.keys():
    patients[patient] = sorted(patients[patient],
                               key=lambda (admission, diag): times[admission])

g = open('results.csv', 'w')
for patient in patients:
    g.write(str(patients[patient]) + '\n')
g.close()

icd9_pairs = [(k, icd9s[k]) for k in icd9s]
icd9_pairs.sort(key=lambda (k, v): -v)
h = open('icd9pairs.csv', 'w')
for pair in icd9_pairs:
    h.write(str(pair) + '\n')
h.close()

output = []
pairs = {}
bmi_low = 0
bmi_high = 0
age_low = 0
age_high = 0
if len(sys.argv) > 2:
    low, high = sys.argv[2].strip().split('-')
    bmi_low = float(low)
    bmi_high = float(high)
if len(sys.argv) > 3:
    low, high = sys.argv[3].strip().split('-')
    age_low = int(low)
    age_high = int(high)
for patient in patients.keys():
    if age_low > 0:
        if to_age(patient) < age_low or to_age(patient) >= age_high:
            continue
    elif bmi_low > 0:
        if to_bmi(patient) < bmi_low or to_bmi(patient) >= bmi_high:
            continue
    data = patients[patient]
    i = 0
    #tp = ('START', (0, icd9text[data[0][1]]))
    tp = ('START', (0, data[0][1]))
    if tp not in pairs:
        pairs[tp] = 0
    pairs[tp] += 1
    while i < len(data) - 1:
        tp = ((i, data[i][1]), (i + 1, data[i + 1][1]))
        if tp not in pairs:
            pairs[tp] = 0
        pairs[tp] += 1
        i += 1
    tp = ((i, data[i][1]), 'DEATH')
    if tp not in pairs:
        pairs[tp] = 0
    pairs[tp] += 1
k = open(sys.argv[1], 'w')
for pair in pairs.keys():
    if pairs[pair] > 4:
        k.write('%s [%d] %s\n' % (str(pair[0]), pairs[pair], str(pair[1])))
k.close()
