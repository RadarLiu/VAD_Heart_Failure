import sys
import operator
from collections import *

database = list()
maxCount = 0
alpha = 0.9
sim_choice = 1
top_n = 10
method = 3

# jaccard similarity
def jaccardSimilarity(method, l1, l2, offset=0, ):
	'''
	@method: which method to use to calculate similarity
	@l1: frequent pattern
	@l2: patient diagnoses
	@offset: first timestamp in frequent pattern
	'''
	if method == 1:
		delta = abs((l1[1] - offset) - l2[1]) 	# penalty on time delta
		# if l1[1] == offset:	# first admission, high penalty
		# 	delta = 3
		return float(len(set(l1[0])&set(l2[0]))) / len(set(l1[0])|set(l2[0])) / (delta + 2)
	elif method == 2:
		return float(len(set(l1[0])&set(l2[0]))) / len(set(l1[0])|set(l2[0]))
	elif method == 3:
		return float(len(set(l1[1])&set(l2[1]))) / len(set(l1[1])|set(l2[1]))
	

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
	if set(pattern).issubset(set(patient)):  # patient contains pattern
		return float(len(pattern))/len(patient)
	else:
		return 0


def calSimilarity(i, pattern, patient):
	if len(pattern['sequence']) <= len(patient):
		return 0
	sim = 0

	if method == 1:
		# Method 1: Naive matching, scan admissions and match one by one
		for i, diagnosis in enumerate(patient):
			if sim_choice == 1:
				sim += jaccardSimilarity(1, pattern['sequence'][i], diagnosis, pattern['sequence'][0][1])
			else:
				sim += containSimilarity(pattern['sequence'][i], diagnosis)
	elif method == 2:  
		# Method 2: 2 pointers moving 
		pattern_index = 0
		patient_index = 0
		offset = pattern['sequence'][0][1]
		for patient_index, diagnosis in enumerate(patient):
			# find the best index (timestamp) in frequent pattern that matches current diagnosis
			while pattern_index < len(pattern['sequence']) - 1 and abs((pattern['sequence'][pattern_index][1] - offset) - diagnosis[1]) > abs((pattern['sequence'][pattern_index+1][1] - offset) - diagnosis[1]):
				pattern_index += 1
					
			if pattern_index >= len(pattern['sequence']):
				return 0
			else:
				sim += jaccardSimilarity(2, pattern['sequence'][pattern_index], diagnosis)
				pattern_index += 1
	elif method == 3:
		# Method 3: hashtable, cluster on timestamp
		patient_dict = dict()
		pattern_dict = dict()
		offset = pattern['sequence'][0][1]
		for diagnosis in patient:
			timestamp = diagnosis[1]
			if timestamp in patient_dict:
				patient_dict[timestamp] += list(diagnosis[0])
			else:
				patient_dict[timestamp] = list(diagnosis[0])

		for diagnosis in pattern['sequence'][:-1]:
			timestamp = diagnosis[1] - offset
			if timestamp in pattern_dict:
				pattern_dict[timestamp] += list(diagnosis[0])
			else:
				pattern_dict[timestamp] = list(diagnosis[0])

		if len(pattern_dict) < len(patient_dict):
			return 0

		sorted_pattern_dict = sorted(pattern_dict.items(), key=operator.itemgetter(0))
		sorted_patient_dict = sorted(patient_dict.items(), key=operator.itemgetter(0))

		pattern_index = 0
		for patient_index, diagnosis in enumerate(sorted_patient_dict):
			# find the best index (timestamp) in frequent pattern that matches current diagnosis
			while pattern_index < len(sorted_pattern_dict) - 1 and abs(sorted_pattern_dict[pattern_index][0] - diagnosis[0]) > abs(sorted_pattern_dict[pattern_index+1][0] - diagnosis[0]):
				pattern_index += 1
					
			if pattern_index >= len(sorted_pattern_dict):
				return 0
			else:
				sim += jaccardSimilarity(3, sorted_pattern_dict[pattern_index], diagnosis)
				pattern_index += 1
		
	score = (alpha * sim + (1-alpha) * pattern['count']/maxCount)	# count between 0-1, sim between 0-1
	return score



# preprocess existing sequential data
with open('spade_diagnose_from_heart_to_death_timestamped_revised.txt') as f:
	for line in f:
		sequence, count = line.strip().split('#SUP: ')
		count = int(count)
		if count > maxCount:
			maxCount = count
		pattern = dict()
		pattern['count'] = count
		pattern['sequence'] = list()
		for s in sequence.split('->'):
			pattern['sequence'].append((s.strip().split('[')[0].strip()[1:-1].split('\" \"'), int(s.strip().split('[')[1][:-1])))
		database.append(pattern)

# match a new patient to current sequential data
# 261
patient = [(['Ac/subac bact endocard','CHF NOS','Atrial fibrillation','Atrial flutter','Protein-cal malnutr NOS','Dis tympanic memb NOS','Mal neo esophagus NEC','DMII wo cmp nt st uncntr'],0)]

# 10124:
# [82021, 42832, 4280, 5990, 2851, 42731, 5859, 99811, 5849, 9980, E8859, 2449, 25000, 4414, 73300, 40390, E8788]
# [51884, 42833, 40391, 42731, 5845, 2767, 486, 25092, 03811, 70705, 5990, 99591, 4168, 32723, 27800, V5413, V1251, 56400]
patient = [(['Intertrochanteric fx-cl', 'Chr diastolic hrt fail', 'CHF NOS', 'Urin tract infection NOS', 'Ac posthemorrhag anemia', 'Atrial fibrillation', 'Chronic kidney dis NOS', 'Hemorrhage complic proc', 'Acute kidney failure NOS', 'Fall from slipping NEC', 'Hypothyroidism NOS', 'DMII wo cmp nt st uncntr', 'Abdom aortic aneurysm', 'Osteoporosis NOS', 'Hy kid NOS w cr kid I-IV', 'Abn react-surg proc NEC'],0),\
(['Acute & chronc resp fail', 'Ac on chr diast hrt fail', 'Hyp kid NOS w cr kid V', 'Atrial fibrillation', 'Ac kidny fai', 'Hyperpotassemia', 'Pneumoni', 'DMII unspf uncntrld', 'Meth susc Staph aur sept', 'Pressure ulce', 'Urin tract infection NOS', 'Sepsis', 'Chr pulmon heart dis NEC', 'Obstructive sleep apnea', 'Obesity NOS', 'Aftrcre traumatic fx hip', 'Hx-ven thrombosis/embols', 'Constipation NOS'],0),
]

# 10174
# [99592,41071,42613,78559,2765,4160,4240,25001,2767]
# [9724,5849,2767,5997,2765,E8583,4019,412,25000]
# [41071,60000,2720,4019,07032,41401,4280,4240,25060,3572,53081,V5867]
# [6823,6983,79093,53081,60001,78820,2809,27651,42789,5849,34982,2763,2762,5859,40310,25002,V4581]
# [42689,E9424,40390,5859,25000,2724,V4581,53081]
patient = [
# ['Severe sepsis', 'Subendo infarc', 'Av block-2nd degree NEC', 'Shock w/o trauma NEC', 'Prim pulm hypertension', 'Mitral valve disorder', 'DMI wo cmp nt st uncntrl', 'Hyperpotassemia'],\
# ['Pois-coronary vasodilat', 'Acute kidney failure NOS', 'Hyperpotassemia', 'Acc poisn-cardiovasc agt', 'Hypertension NOS', 'Old myocardial infarct', 'DMII wo cmp nt st uncntr'],\
(['Subendo infarc', 'BPH w/o urinary obs/LUTS', 'Pure hypercholesterolem', 'Hypertension NOS', 'Hpt B chrn wo cm wo dlta', 'Crnry athrscl natve vssl', 'CHF NOS', 'Mitral valve disorder', 'DMII neuro nt st uncntrl', 'Neuropathy in diabetes', 'Esophageal reflux', 'Long-term use of insulin'],0),\
(['Cellulitis of arm', 'Lichenification', 'Elvtd prstate spcf antgn', 'Esophageal reflux', 'BPH w urinary obs/LUTS', 'Retention urine NOS', 'Iron defic anemia NOS', 'Dehydration', 'Cardiac dysrhythmias NEC', 'Acute kidney failure NOS', 'Toxic encephalopathy', 'Alkalosis', 'Acidosis', 'Chronic kidney dis NOS', 'Ben hy kid w cr kid I-IV', 'DMII wo cmp uncntrld', 'Aortocoronary bypass'],4),
#(['Conduction disorder NEC', 'Adv eff coronary vasodil', 'Hy kid NOS w cr kid I-IV', 'Chronic kidney dis NOS', 'DMII wo cmp nt st uncntr', 'Hyperlipidemia NEC/NOS', 'Aortocoronary bypass', 'Esophageal reflux'],14)\
]

#735
patient = [
(['Iatrogen pulm emb/infarc', 'Surg compl-heart', 'Atrial fibrillation', 'CHF NOS', 'Anemia NOS', 'Crnry athrscl natve vssl'],0),\
(['Ac posthemorrhag anemia', 'Hypovolemia', 'Myelopathy in oth dis', 'Hx of kidney malignancy', 'Acquired absence kidney', 'Hx-ven thrombosis/embols'],28),\
#(['Neoplasm related pain', 'Hypothyroidism NOS', 'Obstructive sleep apnea', 'Hypertension NOS', 'Hyperlipidemia NEC/NOS', 'Hx of kidney malignancy', 'Arthrodesis status', 'Acquired absence kidney', 'Hx antineoplastic chemo', 'Hx of irradiation', 'Path fx oth spcf prt fmr', 'Abn react-surg proc NEC', 'Secondary malig neo skin', 'Secondary malig neo lung', 'Delirium d/t other cond', 'Ch DVT/embl dstl low ext', 'Atrial fibrillation'],33),
]


pattern_scores = dict()
for i, pattern in enumerate(database):
	score = calSimilarity(i, pattern, patient)
	pattern_scores[i] = score
	

# sort and print out top 10 result with scores 
sorted_score = sorted(pattern_scores.items(), key=operator.itemgetter(1), reverse = True)

for index, score in sorted_score[:top_n]:
	print "index: %d\t%f\t%s" % (index, score, database[index])






