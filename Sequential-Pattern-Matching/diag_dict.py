import sys
code_dict = dict()
with open('D_ICD_DIAGNOSES.csv') as f:
	for line in f:
		words = line.split(',')
		code_dict[words[1][1:-1]] = words[2][1:-1]

code_list = list()
raw = sys.argv[1]

for i in raw[1:-1].split(','):
    code_list.append(i)

result = list()
for i in code_list:
	if i in code_dict:
		result.append(code_dict[i])

print result
