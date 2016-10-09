import pandas as pd
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
from sklearn.cluster import AgglomerativeClustering
plt.style.use('ggplot')


def load_data_csv(path):
    return pd.read_csv(path)

def jaccard_distance(a,b):
    a_inter_b = len(set(a[:-3]) & set(b[:-3]))
    a_union_b = len(set(a[:-3]) | set(b[:-3]))
    return 1 - float(a_inter_b)/a_union_b


# def to_life_span(patients):
#     death = pd.to_datetime(patients.DOD) - pd.to_datetime(patients.DOB)
#     return death[death.astype(int)>0]
#
#
# def xy(patients):
#     lifes = to_life_span(patients).tolist()
#     lifes = Counter(live.days/365 for live in lifes)
#     x = sorted(lifes)
#     y = np.array([float(lifes[l]) for l in x])
#     y /= sum(y)
#     return x, y

# procedures = load_data_csv('data/PROCEDURES_ICD.csv')
# vad = procedures[procedures.ICD9_CODE.astype(str).str.startswith('376', na=False)]['SUBJECT_ID'].drop_duplicates()

# vad_patients = heart_fail_patients[heart_fail_patients.SUBJECT_ID.isin(vad)]
# non_vad_patients = heart_fail_patients[heart_fail_patients.SUBJECT_ID.isin(vad)==False]



diagnoses = load_data_csv('data/DIAGNOSES_ICD.csv')
hf_patients_diagnoses = diagnoses[diagnoses.ICD9_CODE.str.startswith('428', na=False)]

patients = load_data_csv('data/PATIENTS.csv')[['SUBJECT_ID', 'GENDER', 'DOB', 'DOD']]
patients['DOD'] = pd.to_datetime(patients.DOD)
patients['DOB'] = pd.to_datetime(patients.DOB)

# number of hf patients: 5232
hf_patients = patients[patients.SUBJECT_ID.isin(hf_patients_diagnoses['SUBJECT_ID'])][patients.DOD.isnull()==False]
hf_patients['life_span'] = (hf_patients.DOD - hf_patients.DOB).dt.days/365
hf_patients = hf_patients[hf_patients.life_span > 0]

hf_patients_diagnoses = diagnoses[diagnoses.SUBJECT_ID.isin(hf_patients['SUBJECT_ID'])]
hf_patients_diagnoses = pd.merge(hf_patients_diagnoses, hf_patients, on='SUBJECT_ID')

# admissions
admission = load_data_csv('data/ADMISSIONS.csv')[['HADM_ID','DISCHTIME', 'ADMITTIME']]
admission['DISCHTIME'] = pd.to_datetime(admission.DISCHTIME)
admission['ADMITTIME'] = pd.to_datetime(admission.ADMITTIME)
admission['stay_time'] = (admission.DISCHTIME - admission.ADMITTIME).dt.days

hf_hos = pd.merge(hf_patients_diagnoses, admission, on='HADM_ID', how='left')
hf_hos_count = hf_hos[['SUBJECT_ID', 'HADM_ID']].groupby('SUBJECT_ID').count().rename(columns=lambda x: 'hos_stay_count')
hf_hos_count = hf_hos_count.reset_index()
hf_summary = pd.merge(hf_hos, hf_hos_count, on='SUBJECT_ID', how='left')

### number of admission distribution
# hos_counts = hf_hos_count['hos_stay_count'].tolist()
# hos_counts = Counter(hos_counts)
# x = sorted(hos_counts)
# y = y = np.array([hos_counts[l] for l in x])
# plt.plot(x, y, '-', color='red')
# plt.show()
#
# ### first admission to death distribution
hf_summary['ad_2_death'] = (hf_summary.DOD - hf_summary.ADMITTIME).dt.days + 1
# hf_ad_2_death = hf_summary[['SUBJECT_ID', 'ad_2_death']].groupby('SUBJECT_ID').max().rename(columns=lambda x: 'first_ad_2_death').reset_index()
# #distribution
# deaths = hf_ad_2_death['first_ad_2_death'].tolist()
# deaths = Counter(deaths)
# x = sorted(deaths)
# y = np.array([deaths[l] for l in x])
# plt.plot(x, y, '-', color='red')
# plt.show()

### clustering on disgnoses per hospital stay HCA
hf_summary['ICD9_CODE'] = hf_summary['ICD9_CODE'].astype(str)
icd9 = hf_summary.groupby(['SUBJECT_ID','HADM_ID','ad_2_death'])['ICD9_CODE'].apply(list).rename(columns=lambda x: 'icd9_list').reset_index()

training_data = []
for index, icd in icd9.iterrows():
    dp = []
    for i in icd[3]:
        if i[0] in ['0','1','2','3','4','5','6','7','8','9']:
            dp.append(int(i[:3]))
    if len(dp) != 0:
        dp.append(icd[0])
        dp.append(icd[1])
        dp.append(icd[2])
        training_data.append(dp)

# training_data = training_data[:1000]
distance_matrix = [[0 for i in range(len(training_data))] for j in range(len(training_data))]
for i in range(len(training_data)):
    for j in range(i, len(training_data)):
        d = jaccard_distance(training_data[i],training_data[j])
        distance_matrix[i][j] = d
        distance_matrix[j][i] = d


ad = AgglomerativeClustering(n_clusters=100)
c = ad.fit_predict(distance_matrix)
cluster = [[] for i in range(100)]
cluster_hadm = [[] for i in range(100)]
for i in range(len(c)):
    cluster[c[i]].append(training_data[i][-1])
    cluster_hadm[c[i]].append(training_data[i][-2])

for i in range(100):
    print str(i) + "\t" + str(np.mean(cluster[i])) + "\t" + str(np.std(cluster[i])) + "\t" + str(len(cluster[i]))

shortest_lives = cluster_hadm[73]
shortest_icd9 = []
shortest_diagnoses_length = []
for x in training_data:
    if x[-2] in shortest_lives:
        shortest_icd9 += x[:-3]
        shortest_diagnoses_length.append(len(x)-3)

longest_lives = cluster_hadm[98]
longest_icd9 = []
longest_diagnoses_length = []
for x in training_data:
    if x[-2] in longest_lives:
        longest_icd9 += x[:-3]
        longest_diagnoses_length.append(len(x)-3)

# hf_hos_tot_days = hf_hos[['SUBJECT_ID','stay_time']].groupby('SUBJECT_ID').sum().rename(columns=lambda x: 'hos_tot_days')
# hf_hos_mean_days = hf_hos[['SUBJECT_ID','stay_time']].groupby('SUBJECT_ID').mean().rename(columns=lambda x: 'hos_mean_days')
#
# heart_fail_patients = heart_fail_patients.reset_index()
# hf_hos_count = hf_hos_count.reset_index()
# hf_hos_tot_days = hf_hos_tot_days.reset_index()
# hf_hos_mean_days = hf_hos_mean_days.reset_index()
#
# hf_hos_lifespan = pd.merge(pd.merge(pd.merge(heart_fail_patients, hf_hos_count, on='SUBJECT_ID') ,hf_hos_tot_days,on='SUBJECT_ID'), hf_hos_mean_days, on='SUBJECT_ID')
#
# print hf_hos_lifespan
#
# cor1 = np.corrcoef(hf_hos_lifespan.life_span,hf_hos_lifespan.hos_stay_count)
# print cor1
# cor2 = np.corrcoef(hf_hos_lifespan.life_span,hf_hos_lifespan.hos_tot_days)
# print cor2
# cor3 = np.corrcoef(hf_hos_lifespan.life_span,hf_hos_lifespan.hos_mean_days)
# print cor3

### Original data
# plot(heart_fail_patients)
# plot(vad_patients)
# plot(non_vad_patients)
# plt.show()

### Over sampling
# x, y = xy(vad_patients)
# plt.plot(x, y, '-', color='red')
# x, y = xy(non_vad_patients)
# plt.plot(x, y, '-', color='green')
# plt.show()