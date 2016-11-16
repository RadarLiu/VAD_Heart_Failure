diagnosis_cluster = {}
procedure_cluster = {}
patients_bmi = {}
patients_age = {}

with open('AppendixASingleDX.txt') as f:
    lines = f.readlines()[4:]
    last_cluster = ''
    for line in lines:
        if line == '\n':
            continue
        if line[0] != ' ':
            idx = 0
            while line[idx] == ' ' or (line[idx] >= '0' and line[idx] <= '9'):
                idx += 1
            last_cluster = line.strip()[idx:]
        else:
            codes = line.strip().split()
            for code in codes:
                diagnosis_cluster[code] = last_cluster

with open('AppendixBSinglePR.txt') as f:
    lines = f.readlines()[4:]
    last_cluster = ''
    for line in lines:
        if line == '\n':
            continue
        if line[0] != ' ':
            idx = 0
            while line[idx] == ' ' or (line[idx] >= '0' and line[idx] <= '9'):
                idx += 1
            last_cluster = line.strip()[idx:]
        else:
            codes = line.strip().split()
            for code in codes:
                procedure_cluster[code] = last_cluster

with open('bmi_out.txt') as f:
    lines = f.readlines()
    for line in lines:
        patient, bmi = line.strip().split()
        patients_bmi[patient] = float(bmi)

with open('PATIENTS.csv') as f:
    lines = f.readlines()[1:]
    for line in lines:
        line = line.strip().split(',')
        if line[4] == '' or line[3] == '':
            continue
        birth = int(line[3][:4])
        death = int(line[4][:4])
        if birth >= death:
            continue
        patients_age[line[1]] = death - birth

def to_diagnose_text(code):
    if code in diagnosis_cluster:
        return diagnosis_cluster[code]
    return code


def to_procedure_text(code):
    if code in procedure_cluster:
        return procedure_cluster[code]
    return code


def to_bmi(patient):
    if patient in patients_bmi:
        return patients_bmi[patient]
    return -1


def to_age(patient):
    if patient in patients_age:
        return patients_age[patient]
    return -1
