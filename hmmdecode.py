import pickle
import math

#script,path=argv

modelfile=open('hmmmodel.txt','rb')
outputfile=open('hmmoutput.txt','w')
decode_it=open('catalan_corpus_dev_raw.txt')


tag_count=pickle.load(modelfile)
word_tag_count=pickle.load(modelfile)
tag_tag_count=pickle.load(modelfile)

raw_data=decode_it.read().replace("\r", " ").replace("\t", " ").split('\n')

# calculating emission probability
em_prob={}
num_tags=len(tag_count)

for line in raw_data:
    splitted_line=line.split()

    for word in splitted_line:

        #Handling unseen words for emission probability
        if word in word_tag_count:
            if word not in em_prob:
                em_prob[word] = {}
             #was observed in corpus
            for tag in word_tag_count[word]:
                if tag not in em_prob[word]:
                    em_prob[word][tag]={}
                    em_prob[word][tag]=math.log(1.0*word_tag_count[word][tag]/tag_count[tag],2)

Q=[]

for key in tag_count:
    Q.append(key)
for line in raw_data:
    probability = {}
    backpointer = {}
    splitted_line=line.split()
    t=1
    T=len(splitted_line)
    prev_word = ''
    for word in splitted_line:
    
        # Initialization step at t=1
        
        if t==1:                    #for 1st word of sentence
            if word in em_prob:    #not unseen word, but transitions could be unseen so smoothen in formula
                for q in em_prob[word]:
                    if q not in probability:
                        probability[q]={}
                    if q not in backpointer:
                        backpointer[q]={}
                    if q in tag_tag_count['qnot']:
                        numerator=tag_tag_count['qnot'][q]
                    else:
                        numerator=0
                    probability[q][1] = math.log((numerator+1.0)/(sum(tag_tag_count['qnot'].values())+ num_tags),2) + em_prob[word][q]
                    backpointer[q][1] ='qnot'
            else:    #unseen word therefore formula different
                for q in Q:
                    if q not in probability:
                        probability[q]={}
                    if q not in backpointer:
                        backpointer[q]={}
                    if q in tag_tag_count['qnot']:
                        numerator = tag_tag_count['qnot'][q]
                    else:
                        numerator = 0
                    probability[q][1]=math.log((numerator+1.0)/(sum(tag_tag_count['qnot'].values())+ num_tags),2)
                    backpointer[q][1]='qnot'
                    
                 #Recursion step for the remaining time points
                 
            prev_word=word
        elif t<=T:          #for rest of the words of sentence from 2 to T
            if word in em_prob:
                for q in em_prob[word]:
                    max_prod = float('-inf')
                    max_tag = ''
                    max_prod_backptr = float('-inf')
                    if q not in probability:
                        probability[q]={}
                    if q not in backpointer:
                        backpointer[q]={}
                    if prev_word in em_prob:
                        taglist=em_prob[prev_word]
                    else:
                        taglist=Q
                    for qprime in taglist: #qprime - prev tags
                        if q in tag_tag_count[qprime]:
                            numerator = tag_tag_count[qprime][q]
                        else:
                            numerator = 0
                        if (t-1) in probability[qprime]:
                            prod_for_backptr=probability[qprime][t-1]+math.log(((numerator+1.0)/(sum(tag_tag_count[qprime].values())+ num_tags)),2)
                            prod=prod_for_backptr+em_prob[word][q]
                            if prod>max_prod:
                                max_prod=prod
                            if max_prod_backptr<prod_for_backptr:
                                max_prod_backptr=prod_for_backptr
                                max_tag=qprime
                    probability[q][t]=max_prod
                    backpointer[q][t]=max_tag
            else:       #case unseen words-handling
                 for q in Q:
                    max_prod = float('-inf')
                    max_tag = ''
                    if q not in probability:
                        probability[q]={}
                    if q not in backpointer:
                        backpointer[q]={}
                    if prev_word in em_prob:
                        taglist=em_prob[prev_word]
                    else:
                        taglist=Q
                    for qprime in taglist:
                        if q in tag_tag_count[qprime]:
                            numerator=tag_tag_count[qprime][q]
                        else:
                            numerator=0
                        if t-1 in probability[qprime]:
                            prod=probability[qprime][t-1]+math.log(((numerator+1.0)/(sum(tag_tag_count[qprime].values())+num_tags)),2)
                            if prod>max_prod:
                                max_prod=prod
                                max_tag=qprime
                    backpointer[q][t]=max_tag
                    probability[q][t]=max_prod
            prev_word=word
        t+=1
        
    #Termination step
    
    max_last_state=float('-inf')
    most_probable_tag=''
    splitted_line.reverse()
    for q in probability:
        if T in probability[q]:
            if probability[q][T]>max_last_state:
                max_last_state=probability[q][T]
                most_probable_tag=q
    ts=T
    for index,word in enumerate(splitted_line):
        prev_tag=backpointer[most_probable_tag][ts]
        word+='/'+most_probable_tag
        splitted_line[index]=word
        most_probable_tag=prev_tag
        ts-=1
    splitted_line.reverse()
    result=(' ').join(splitted_line)+'\n'
    outputfile.write(result)
