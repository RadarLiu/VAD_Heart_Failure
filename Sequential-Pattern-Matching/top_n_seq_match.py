#f_train = open("spade_diagnose_from_heart_to_death_timestamped_revised.train","r")
#f_test_in = open("spade_diagnose_from_heart_to_death_timestamped_revised.test","r")
f_train = open("spade_diagnose_from_heart_to_death_timestamped_revised.txt","r")
f_test_in = open("spade_in_ready_diagnose_from_heart_to_death_timestamp_revised.csv","r")
f_test_out = open("test_result.txt","w")

#data structure definition of sequence:
# [[([diagnoses], time), ([diagnoses], time),], support]

data = []
tms = 0
for line in f_train:
    try:
        seq_and_sup = []
        seq = []
        hospital_visits_plus_death = line.split('->')
        for i in range(0, len(hospital_visits_plus_death) - 1): #not including the "death tail part"
            transact = hospital_visits_plus_death[i].strip()
            diagnoses_and_timestamp = transact.split('" ')
            diagnose_list = []
            for j in range(0, len(diagnoses_and_timestamp) - 1):
                diagnose_list.append(diagnoses_and_timestamp[j][1:])
            #append : ([diagnoses], time)
            seq.append((diagnose_list, diagnoses_and_timestamp[len(diagnoses_and_timestamp) - 1]))
        last_transaction = hospital_visits_plus_death[len(hospital_visits_plus_death) - 1]
        fields = last_transaction.split("#SUP:")
        death = fields[0].strip()
        sup = int(fields[1].strip())
        death_timestamp = death.split(" ")[1]
        seq.append(("DEATH", death_timestamp))
        seq_and_sup.append(seq)    
        seq_and_sup.append(sup)
        data.append(seq_and_sup)
    except:
        pass #just abandon mal-format data
    tms += 1
    #if (tms == 4105):
    #    print seq_and_sup
    #else:
    #    print tms
f_train.close()

# now, the list data is like: 
'''
[[(['Chr diastolic hrt fail'], '[7]'), ('DEATH', '[8]')], 5]
[[(['Ac on chr syst hrt fail'], '[6]'), ('DEATH', '[6]')], 6]
[[(['Ac on chr diast hrt fail'], '[5]'), ('DEATH', '[5]')], 5]
[[(['Ac on chr diast hrt fail'], '[4]'), ('DEATH', '[4]')], 7]
[[(['Ac on chr diast hrt fail'], '[3]'), ('DEATH', '[4]')], 5]
[[(['Diastolc hrt failure NOS'], '[3]'), ('DEATH', '[3]')], 6]
[[(['Chr systolic hrt failure'], '[3]'), ('DEATH', '[3]')], 9]
[[(['Ac on chr diast hrt fail'], '[2]'), ('DEATH', '[3]')], 7]
[[(['Ac on chr syst hrt fail'], '[2]'), ('DEATH', '[2]')], 7]
[[(['Chr systolic hrt failure'], '[2]'), ('DEATH', '[3]')], 5]
[[(['CHF NOS'], '[35]'), ('DEATH', '[35]')], 7]
[[(['CHF NOS'], '[0]'), (['CHF NOS'], '[0]'), (['CHF NOS', 'DMII wo cmp nt st uncntr'], '[1]'), ('DEATH', '[1]')], 5]
'''
#need to parse the raw patient data (with embedded timestamp) into the same format

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

data_test = []  
#corresponding to list "data" above, but containing only [([diagnoses], time), ([diagnoses], time),]
timestamp = ''
tms = 0
for line in f_test_in:
    #if not ('989999' in line): continue   #does not require death...
    #make sure that heart-related problems occur in the first set
    first_neg_one = line.index('-1')
    first_part = line[0:first_neg_one]
    #if not ('428' in first_part): continue  #just don't skip test data...

    seq = []
    list_diagnoses = []
    fields = line.split(' ')   #line: a single line with multiple transactions!
    length = len(fields)
    content = ''
    if (length < 6):
        continue
    for i in range(0, length - 1):
        try:
            label = int(fields[i])  #timestamp98label
            if (label == -1):
                seq.append((list_diagnoses, '[' + timestamp + ']'))
                list_diagnoses = []
                #if (i < length - 3):
                #    content += '-> '
            else:
                #extract timestamp from "9timestamp9" in the beginning of every item in this transaction
                label_s = str(label)
                delim_idx = label_s.index('98')
                timestamp = label_s[0:delim_idx]
                timestamp = str(int(timestamp) - 1) #there is a "1 offset in pre-porcessing"
                #print timestamp
                diagnose_name = label_s[delim_idx + 2 : len(label_s)]
                #if (tms < 2): print diagnose_name
                list_diagnoses.append(diagnose_dict[str(diagnose_name)])
                #content += ('\"' + diagnose_dict[str(diagnose_name)] + '\" ')
        except: pass
    data_test.append(seq)
    tms += 1
    #if (tms < 2):
    #    print seq

#now data_test looks like: (each line)
'''
[(['CHF NOS', 'Iatrogenc hypotnsion NEC', 'Chr airway obstruct NEC', 
    'Pleurisy w/o effus or TB', 'Intestinal obstruct NEC', 'Acute kidney failure NOS'], '[0]'), 
(['Chr blood loss anemia', 'Hypertension NOS', 'Crnry athrscl natve vssl', 'CHF NOS', 
    'Noninfect lymph dis NEC', 'Iatrogenc hypotnsion NEC', 'Pneumoni', 'Chr airway obstruct NEC', 
    'Acute respiratry failure', 'Gastrointest hemorr NOS', 'Other postop infection', 
    'Prim TB pleurisy-no exam', 'Ac bulbar polio-type 1', 'Ac bulbar polio-type 2'], '[2]'), 
(['Anemia NOS', 'Idio periph neurpthy NOS', 'Subendo infarc', 'Crnry athrscl natve vssl', 
    'Prim cardiomyopathy NEC', 'CHF NOS', 'Chr airway obstruct NEC', 'Food/vomit pneumonitis', 
    'Acute & chronc resp fail', 'Acute kidney failure NOS', 'Septic shock', 'Severe sepsis', 
    'Prim TB pleurisy-no exam', 'Ac bulbar polio-type 1', 'Ac bulbar polio-type 2'], '[3]'), 
(['Hyposmolality', 'Anoxic brain damage', 'Hypertension NOS', 'Crnry athrscl natve vssl', 
    'Atrial fibrillation', 'CHF NOS', 'Crbl emblsm w infrct', 'Pseudomonal pneumonia', 
    'Bronchiectas w/o ac exac', 'Acute & chronc resp fail', 'Prim TB pleurisy-no exam', 
    'Ac bulbar polio-type 2'], '[3]'), 
(['DEATH'], '[3]')]
'''

#for testing, now (10.26) we lack metrics, so we can only find the top k match, and "see" 
#the matched sequence quality

