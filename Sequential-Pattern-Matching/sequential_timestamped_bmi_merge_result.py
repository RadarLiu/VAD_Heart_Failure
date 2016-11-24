import sys
import operator
from collections import *

database = list()
maxCount = 0
alpha = 0.9
sim_choice = 1
top_n = 10

# jaccard similarity
def jaccardSimilarity(l1, l2):
    #note: (11.2) avoid using the last element in l1! it is timestamp!
    l11 = l1[0 : len(l1) - 1]
    return float(len(set(l11)&set(l2))) / len(set(l11)|set(l2))

"""
def cosineSimilarity(l1, l2):
    sim = 0
    for d in l2:
        if d in l1:
            sim += 1
    for d in l1:
        if d not in l2:
            sim -= 1
    return sim
"""

# will only have non-zero score if patient's diagnoses totally cover diagnoses in the sequence
def containSimilarity(pattern, patient):
    #avoid timestamp in pattern!
    ppattern = pattern[0 : len(pattern) - 1]
    if set(pattern).issubset(set(patient)):  # patient contains pattern
        return float(len(pattern))/len(patient)
    else:
        return 0


def calSimilarity(pattern, patient):
    #note: (11.2) avoid using the last element in pattern['sequence'][i]! it is timestamp!
    #if len(pattern['sequence']) <= len(patient):

    if len(pattern['sequence']) < len(patient):  #please at least allow self-retrieving in sanity check...
        return 0
    sim = 0
    if (int(patient[0]) != int(pattern['bmi_bin'])):
        return 0.0
    for i, diagnosis in enumerate(patient):
        if (i == 0):
            continue
        if sim_choice == 1:
            sim += jaccardSimilarity(pattern['sequence'][i], diagnosis)
        else:
            sim += containSimilarity(pattern['sequence'][i], diagnosis)
    score = (alpha * sim + (1-alpha) * pattern['count']/maxCount)  # count between 0-1, sim between 0-1
    return score


#tuplenize every diagnose in diag_list with the score
def make_tuples(diag_list, score):
    ans_list = []
    for item in diag_list:
        ans_list.append((item, score))
    return ans_list


#For 11.2:
# for testing: create the testing instance here, put the timestamp in comment,
# format for patients is the same as before
# in parsing, keep track of timestamps separately, do not involve it in any matching,
# just put it back in output!

# preprocess existing sequential data
with open('spade_diagnose_from_heart_to_death_final_revised_with_bmi.out') as f:
    for line in f:
        sequence, count = line.strip().split('#SUP: ')
        count = int(count)
        if count > maxCount:
            maxCount = count
        pattern = {}
        pattern['count'] = count
        pattern['sequence'] = list()
        tms = 0
        for s in sequence.split('->'):
            tms += 1
            if (tms == 1):
                pattern['bmi_bin'] = int(s.strip())
                continue
            sr = s[0:s.index('[')]
            timestamp = s[s.index('[') : s.index(']') + 1]
            diagnose_timestamp_list = sr.strip()[1:-1].split('\" \"')
            diagnose_timestamp_list.append(timestamp)
            pattern['sequence'].append(diagnose_timestamp_list) 
            #a timestamp is attached after every transaction
            #avoid this in pattern matching!
            #but it is easy to enable timestamp matching in this way.....
        database.append(pattern)

# match a new patient to current sequential data
# 261
patient = [2, ['Ac/subac bact endocard','CHF NOS','Atrial fibrillation','Atrial flutter','Protein-cal malnutr NOS','Dis tympanic memb NOS','Mal neo esophagus NEC','DMII wo cmp nt st uncntr']]

# 1024:[51884, 42833, 40391, 42731, 5845, 2767, 486, 25092, 03811, 70705, 5990, 99591, 4168, 32723, 27800, V5413, V1251, 56400]
# [82021, 42832, 4280, 5990, 2851, 42731, 5859, 99811, 5849, 9980, E8859, 2449, 25000, 4414, 73300, 40390, E8788]
# patient = [['Intertrochanteric fx-cl', 'Chr diastolic hrt fail', 'CHF NOS', 'Urin tract infection NOS', 'Ac posthemorrhag anemia', 'Atrial fibrillation', 'Chronic kidney dis NOS', 'Hemorrhage complic proc', 'Acute kidney failure NOS', 'Fall from slipping NEC', 'Hypothyroidism NOS', 'DMII wo cmp nt st uncntr', 'Abdom aortic aneurysm', 'Osteoporosis NOS', 'Hy kid NOS w cr kid I-IV', 'Abn react-surg proc NEC'],\
# ['Acute & chronc resp fail', 'Ac on chr diast hrt fail', 'Hyp kid NOS w cr kid V', 'Atrial fibrillation', 'Ac kidny fai', 'Hyperpotassemia', 'Pneumoni', 'DMII unspf uncntrld', 'Meth susc Staph aur sept', 'Pressure ulce', 'Urin tract infection NOS', 'Sepsis', 'Chr pulmon heart dis NEC', 'Obstructive sleep apnea', 'Obesity NOS', 'Aftrcre traumatic fx hip', 'Hx-ven thrombosis/embols', 'Constipation NOS']
# ]

#patient = [2, ['Intertrochanteric fx-cl', 'Chr diastolic hrt fail', 'CHF NOS', 'Urin tract infection NOS', 'Ac posthemorrhag anemia', 'Atrial fibrillation', 'Chronic kidney dis NOS', 'Hemorrhage complic proc', 'Acute kidney failure NOS', 'Fall from slipping NEC', 'Hypothyroidism NOS', 'DMII wo cmp nt st uncntr', 'Abdom aortic aneurysm', 'Osteoporosis NOS', 'Hy kid NOS w cr kid I-IV', 'Abn react-surg proc NEC'],\
#['Acute & chronc resp fail', 'Ac on chr diast hrt fail', 'Hyp kid NOS w cr kid V', 'Atrial fibrillation', 'Ac kidny fai', 'Hyperpotassemia', 'Pneumoni', 'DMII unspf uncntrld', 'Meth susc Staph aur sept', 'Pressure ulce', 'Urin tract infection NOS', 'Sepsis', 'Chr pulmon heart dis NEC', 'Obstructive sleep apnea', 'Obesity NOS', 'Aftrcre traumatic fx hip', 'Hx-ven thrombosis/embols', 'Constipation NOS']
#]

#patient = [2, ['Anemia NOS', 'Ac/subac bact endocard', 'CHF NOS', 'Pulmonary collapse', 'Pain in limb'],\
#['Ac/subac bact endocard', ]\
#]

# 10174
# [99592,41071,42613,78559,2765,4160,4240,25001,2767]
# [9724,5849,2767,5997,2765,E8583,4019,412,25000]
# [41071,60000,2720,4019,07032,41401,4280,4240,25060,3572,53081,V5867]
# [6823,6983,79093,53081,60001,78820,2809,27651,42789,5849,34982,2763,2762,5859,40310,25002,V4581]
# [42689,E9424,40390,5859,25000,2724,V4581,53081]
# patient = [['Severe sepsis', 'Subendo infarc', 'Av block-2nd degree NEC', 'Shock w/o trauma NEC', 'Prim pulm hypertension', 'Mitral valve disorder', 'DMI wo cmp nt st uncntrl', 'Hyperpotassemia'],\
# ['Pois-coronary vasodilat', 'Acute kidney failure NOS', 'Hyperpotassemia', 'Acc poisn-cardiovasc agt', 'Hypertension NOS', 'Old myocardial infarct', 'DMII wo cmp nt st uncntr'],\
# ['Subendo infarc', 'BPH w/o urinary obs/LUTS', 'Pure hypercholesterolem', 'Hypertension NOS', 'Hpt B chrn wo cm wo dlta', 'Crnry athrscl natve vssl', 'CHF NOS', 'Mitral valve disorder', 'DMII neuro nt st uncntrl', 'Neuropathy in diabetes', 'Esophageal reflux', 'Long-term use of insulin'],\
# ['Cellulitis of arm', 'Lichenification', 'Elvtd prstate spcf antgn', 'Esophageal reflux', 'BPH w urinary obs/LUTS', 'Retention urine NOS', 'Iron defic anemia NOS', 'Dehydration', 'Cardiac dysrhythmias NEC', 'Acute kidney failure NOS', 'Toxic encephalopathy', 'Alkalosis', 'Acidosis', 'Chronic kidney dis NOS', 'Ben hy kid w cr kid I-IV', 'DMII wo cmp uncntrld', 'Aortocoronary bypass'],
# ['Conduction disorder NEC', 'Adv eff coronary vasodil', 'Hy kid NOS w cr kid I-IV', 'Chronic kidney dis NOS', 'DMII wo cmp nt st uncntr', 'Hyperlipidemia NEC/NOS', 'Aortocoronary bypass', 'Esophageal reflux']\
# ]


#For 11.2:
# for testing: create the testing instance here, put the timestamp in comment,
# format for patients is the same as before
# in parsing, keep track of timestamps separately, do not involve it in any matching,
# just put it back in output!

#For sanity check
#"CHF NOS" [0] -> "Cardiac dysrhythmias NEC" [0] -> "DEATH" [0] #SUP: 8
#patient = [['CHF NOS'],\
#['Atrial fibrillation'],
#['DEATH']]


pattern_scores = dict()
for i, pattern in enumerate(database):  #i is "iteration number"
    score = calSimilarity(pattern, patient)
    pattern_scores[i] = score
    

# sort and print out top 10 result with scores 
sorted_score = sorted(pattern_scores.items(), key=operator.itemgetter(1))
sorted_score.reverse()

ans = sorted_score[:top_n]

#old print
for index, score in ans:
    print "%f\t%s" % (score, database[index])

print "-------------------------------------------------------------"

#find clusters in scores....
#method:
#1. find max and min score
#2. watch diff : compare with (max - min), when > 30% * (max - min): drop!
#This is not a very robust heuristic, but at least it works...

min = 1000
max = 0
for index, score in ans:
    if min > score: min = score
    if max < score: max = score
var = max - min

#print 'var = ', var

#ans:
#list of tuple(index, score)
last = 0
for i in range(0, top_n):
    #print ans[i + 1][1] - ans[i][1]
    if (i == top_n - 1) or (ans[i][1] - ans[i + 1][1] > 0.3 * var):
        merged_list = [] #this is a list of list
        for j in range(last, i + 1):  #don't leave out this "+1"!!
            index = ans[j][0]
            score = ans[j][1]
            tmp_list = database[index]['sequence']
            for k in range(0, len(tmp_list)):
                if k < len(merged_list):
                    #merge diagnose set (actually a list)
                    for diagnose in tmp_list[k]:
                        #if '[' in diagnose: continue #ignore timestamp ???
                        found = False
                        for r in range(0, len(merged_list[k])):  #do not use iterator...  iterator is not a reference to the old object when given new value...(because this is iterating whiel updating!!!)
                            diagnose_merged_tuple = merged_list[k][r]
                            if diagnose_merged_tuple[0] == diagnose: #diagnose name match
                                merged_list[k][r] = (diagnose_merged_tuple[0], diagnose_merged_tuple[1] + score)
                                found = True
                                break
                        if not found:
                            merged_list[k].append((diagnose, score))
                else:
                    merged_list.append(make_tuples(tmp_list[k], score))
        last = i + 1
        #post processing: find "best" timestamps in each diagnose set...
        new_merged_list = []
        for diagnose_list in merged_list:
            timestamp_list = []
            no_timestamp_list = []
            for diagnose_tuple in diagnose_list:
                if '[' in diagnose_tuple[0]:
                    timestamp_list.append(diagnose_tuple)
                else:
                    no_timestamp_list.append(diagnose_tuple)
            #normalize over no_timestamp_list
            sum_score = 0
            for diagnose_tuple in no_timestamp_list:
                sum_score += diagnose_tuple[1]
            for k in range(0, len(no_timestamp_list)): #again, do not use iterator if we expect to update this list!
                no_timestamp_list[k] = (no_timestamp_list[k][0], no_timestamp_list[k][1] / sum_score)
            #insert the best timestamp
            timestamp_list.sort(key = lambda tuple : tuple[1], reverse=True)
            no_timestamp_list.append(timestamp_list[0][0])
            new_merged_list.append(no_timestamp_list)
        #pruning and cut-off (example: using 20% cut-off)
        cut_off_list = [] #this is the "new discoveries"
        retained_list = [] #these are the survivors
        for diagnose_list in new_merged_list:
            reset_retained = True #means a new list in retained_list
            reset_cut_off = True
            for k in range(0, len(diagnose_list) - 1): #the last one is timestamp
                diagnose_tuple = diagnose_list[k]
                #print diagnose_tuple[0]
                if diagnose_tuple[1] >= 0.2: #the retained
                    retained_target = None
                    if reset_retained:
                        reset_retained = False
                        retained_target = []
                        retained_target.append(diagnose_list[len(diagnose_list) - 1]) #timestamp
                        retained_list.append(retained_target)
                    else:
                        retained_target = retained_list[len(retained_list) - 1]
                    retained_target.append(diagnose_tuple)
                else:
                    cut_off_target = None
                    if reset_cut_off:
                        reset_cut_off = False
                        cut_off_target = []
                        cut_off_target.append(diagnose_list[len(diagnose_list) - 1]) #timestamp
                        cut_off_list.append(cut_off_target)
                    else:
                        cut_off_target = cut_off_list[len(cut_off_list) - 1]
                    cut_off_target.append(diagnose_tuple)
        #final formatting: put timestamp at the end of each diagnose set(list)
        for diagnose_list in retained_list:
            diagnose_list.append(diagnose_list.pop(0))
        for diagnose_list in cut_off_list:
            diagnose_list.append(diagnose_list.pop(0))
        print retained_list
        print cut_off_list
        print '\n'
