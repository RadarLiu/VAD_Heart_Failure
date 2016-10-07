#create lab dict
fd = open('D_LABITEMS.csv', 'r')
lab_dict = {}
for line in fd:
    fields = line.split(',')
    itemId = fields[1]
    try:
        itemId = str(int(itemId))
        label = fields[2]
        label = label[1 : len(label) - 1]
        lab_dict[itemId] = label
    except: pass
fd.close()
#convert data
f1 = open('spade_out_lab_abnormal.txt', 'r')
f2 = open('spade_lab_abnormal(final).txt', 'w')
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
                content += ('\"' + lab_dict[str(label)] + '\" ')
        except: pass
    content += (fields[length - 2] + ' ' + fields[length - 1])
    if ('->' in content):
        f2.write(content)
f1.close()
f2.close()
