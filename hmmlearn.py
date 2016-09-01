from sys import argv
import re
import pickle

script,path=argv

file = open(path,'r')

words=file.read()
words=words.replace("\r", "")
words=words.replace("\t", " ")

listofwords=words.replace("\n"," ").split(' ')

diction={}

for word in listofwords:
    if word=='':
        continue
    if word not in diction:
        diction[word]=1
    else:
        diction[word]+=1
tag_count={}

word_tag_count={}

for ele in diction:
    try:
         word,tag=re.split('/(?=[A-Z0-9][A-Z0-9]$)',ele)
         if tag in tag_count:
             tag_count[tag] += diction[ele]
         else:
             tag_count[tag] = diction[ele]
         if word in word_tag_count:
             word_tag_count[word][tag] = diction[ele]
         else:
             word_tag_count[word]={}
             word_tag_count[word][tag] = diction[ele]
    except:
        print '@@@Problem in split'
        print ele.rstrip('\r\n')
num_tags=len(tag_count)
listofwords2=words.split('\n')
tag_tag_count={}
cur_tag='qnot'

for index, line in enumerate(listofwords2):
    splitted_line=line.replace("\n"," ").split()
    cur_tag='qnot'
    for elem in splitted_line:
        next_word,next_tag=re.split("/(?=[A-Z0-9]{2}$)",elem.strip())
        if cur_tag not in tag_tag_count:
            tag_tag_count[cur_tag]={}
        if next_tag not in tag_tag_count[cur_tag]:
            tag_tag_count[cur_tag][next_tag]=0
        tag_tag_count[cur_tag][next_tag]+=1
        cur_tag=next_tag

modelfile=open('hmmmodel.txt','wb')
pickle.dump(tag_count,modelfile)
pickle.dump(word_tag_count,modelfile)
pickle.dump(tag_tag_count,modelfile)
modelfile.close()
