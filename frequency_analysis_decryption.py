import random
import collections
import _abcoll
##Setup some base parameters
input_text = open('input.txt','r')
frequency_text = open('frequency.txt', 'r')

alph =['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

cypher_alph = ['V', 'N', 'T', 'G', 'P', 'H', 'Z', 'K', 'J', 'W', 'S', 'I', 'U', 'A', 'Q', 'Y', 'M', 'R', 'L', 'E', 'C', 'O', 'F', 'B', 'D', 'X']

correct_guess= {}
for a in range(len(alph)):
    correct_guess[cypher_alph[a]] = alph[a]

input_text = input_text.read()
input_text = input_text.lower()
frequency_text = frequency_text.read()
frequency_text = frequency_text.lower()
## Code in this section is used to create an encrypted document.  I am using a the same random alphabet ever time for testing purposes
def random_alph(alph):
    cypher_alph=[]
    for let in alph:
        cypher_alph.append(let.upper())
    random.shuffle(cypher_alph)
    return cypher_alph

def encrypt(alph,cypher_alph,input_text):
    cypher_text=''
    for a in input_text:
        for i in range(len(alph)):
            if a == alph[i]:
                cypher_text += cypher_alph[i]
        if a not in alph:
            cypher_text += a
    return cypher_text





## Start trying to decrypt the document

# functions to setup a base probability and to normalize the probabilites after an update
def start_prob(alph,cypher_lets):
    prob = {}
    for let in alph:
        tmp ={}
        for a in cypher_lets:
            tmp[a]=1./len(cypher_lets)
        prob[let]=tmp
    return prob

def normalize_prob(prob):
    for p in prob:
        val = 0
        for c in prob[p]:
            val += prob[p][c]
        for d in prob[p]:
            prob[p][d] = prob[p][d]/val
    return prob
def frequency_prob(prob,cypher_freq,base_freq):
    return prob

## Make a guess
def best_guess(prob,guess_alph,cypher_freq,base_freq):
    guess1={}
    guess = {}
    missing = []
    guessed = []
    for p in prob:
        best = 0.
        for c in prob[p]:
            if prob[p][c] >= best:
                best = prob[p][c]
                guess1[p]=c,prob[p][c]
    dist=0
    for g in guess1:
        guessed.append([g,guess1[g]])
	## Some letters will have been assigned twice and some not at all we want to pick the most probable ones first
    guessed = sorted(guessed,key=lambda guessed: guessed[1][1])
    inverse_guess = {}
    for g in range(len(guessed)):
        inverse_guess[guessed[g][1][0]]=guessed[g][0]
        guess[guessed[g][0]]=guessed[g][1][0]
	## Check to see what letters are missing
    for c in cypher_alph:		
        if c not in inverse_guess:
            missing.append(c)
	## Add back in the missing letters using the highest frequency letter than hasn't been used
    for f in range(len(cypher_freq)):
        if cypher_freq[f][0] in missing:
            inverse_guess[cypher_freq[f][0]] =base_freq[f][0]

    return [inverse_guess,guess,dist/26]

## Decrypt the text using the best guess
def decrypt(cypher_text,guess):
    decryption = ''
    for c in cypher_text:
        if c in guess:
            decryption+=(guess[c])
        else:
            decryption+=(c)
    return decryption

## Find the frequency of each letter
def frequency(alph,text):
    let_freq=[]
    let_percent = 0.0
    for char in alph:
        let_percent = float(text.count(char))/float(len(text))
        let_freq.append([char,let_percent])
    let_freq = sorted(let_freq,key=lambda let_freq: let_freq[1],reverse=True)
    return let_freq

# find letter groups
def find_pairs(text,alph,num=2):
    tri,pairs, start, end, double, other = [],[],[],[],[],[]
    tmp_dic = {}
    for t in range(len(text)-1):
        if text[t]+text[(t+1)] in tmp_dic:
            tmp_dic[text[t]+text[(t+1)]]+=1
        else:
            tmp_dic[text[t]+text[(t+1)]]=1
    for t in tmp_dic:
        pairs.append([list(t),tmp_dic[t]])
	# sort out special pairs, starting letters, ending letters, and double letters
    for p in range(len(pairs)):
        if pairs[p][0][0] in alph or pairs[p][0][1] in alph:
            if pairs[p][0][0] == pairs[p][0][1]:
                double.append(pairs[p])
            elif pairs[p][0][0] == ' ':
                start.append(pairs[p])
            elif pairs[p][0][1] == (' ' or '.' or ',' or '"' or '!' or '?'):
                end.append(pairs[p])
            else:
                other.append(pairs[p])
	## get letter triplets
    tmp_dic = {}
    for t in range(len(text)-2):
        if text[t]+text[(t+1)]+text[(t+2)] in tmp_dic:
            tmp_dic[text[t]+text[(t+1)]+text[(t+2)]]+=1
        else:
            tmp_dic[text[t]+text[(t+1)]+text[(t+2)]]=1
    for t in tmp_dic:
        tri.append([list(t),tmp_dic[t]])
    double = normalize_pairs(double)
    start = normalize_pairs(start)
    end = normalize_pairs(end)
    other = normalize_pairs(other)
    tri = normalize_pairs(tri)
    return [double,start,end,other,tri]

# sort and crop the list to a certain length
def normalize_pairs(pairs):
    pairs = sorted(pairs,key=lambda pairs: pairs[1],reverse=True)
    pairs = pairs[:50]
    return pairs


#update the probabilites using the frequency of letters and letter groups
def pairs_update_prob(base_pairs,cypher_pairs,prob):
    for p in range(min([len(base_pairs),len(cypher_pairs)])):
        for q in range(min([len(base_pairs),len(cypher_pairs)])):
            for r in range(len(cypher_pairs[q][0][0])):
                if base_pairs[p][0][r] in prob and cypher_pairs[q][0][r] in prob[base_pairs[p][0][r]]:
                    prob[base_pairs[p][0][r]][cypher_pairs[q][0][r]] += (.1/(1+abs(p-q)))**2
                    prob = normalize_prob(prob)
    return prob

#send the groups to be updated
def all_pairs_update(base_pairs,cypher_pairs,prob):
    for p in range(len(base_pairs)):
        prob = pairs_update_prob(base_pairs[p],cypher_pairs[p],prob)
    return prob

cypher_text = encrypt(alph,cypher_alph,input_text)
input_freq = frequency(alph,input_text)
input_pairs = find_pairs(input_text,alph)
#print input_pairs
input_pairs.append(input_freq)
print input_freq
base_freq = frequency(alph,frequency_text)
#base_freq = frequency(alph,input_text)
#print base_freq
#base_pairs = find_pairs(frequency_text,alph)
#base_pairs.append(base_freq)

cypher_freq = frequency(cypher_alph,cypher_text)
cypher_pairs = find_pairs(cypher_text,cypher_alph)
#print cypher_pairs
#cypher_pairs.append(cypher_freq)
prob = start_prob(alph,cypher_alph)
#prob = all_pairs_update(base_pairs,cypher_pairs,prob)
#print prob
guess = best_guess(prob,cypher_alph,cypher_freq,base_freq)
print guess
decrypted_text = decrypt(cypher_text,guess[0])

decrypted_freq = frequency(alph,decrypted_text)
decrypted_pairs = find_pairs(decrypted_text,alph)
decrypted_pairs.append(decrypted_freq)
#decryp_distance = distance(base_pairs,decrypted_pairs)

f = open("encrypted.txt","w")
f.write(cypher_text)
f.close

f = open("decrypted.txt","w")
f.write(decrypted_text)
f.close
