'''This .py file creates catcode and word_sense_children file based on Russian wordnet'''
#please install this package from pip
from wiki_ru_wordnet import WikiWordnet
#the Russian wordnet package which is used
wikiwordnet = WikiWordnet()
'''example of usage for this wordnet
synsets = wikiwordnet.get_synsets('язык') get synsets for word 'язык' in Russian
synset1 = synsets[2]  there are several meaning of this word, choose, for example, third one
for hypernym in wikiwordnet.get_hypernyms(synset1): 
    print({w.lemma() for w in hypernym.get_words()}) print parents (hypernyms) of this word
for hyponym in wikiwordnet.get_hyponyms(synset1):
    print({w.lemma() for w in hyponym.get_words()}) print children of this word
'''
# More detailed documentation of wordnet in Russian https://wiki-ru-wordnet.readthedocs.io/en/latest/

def create_index_file(): #create file with indexes for words in wordnet for which word2vec features exist and create different instances for various meanings
    index_file = open("idx.dat", "w")
    w2v_file = open("ru_w2v.txt")
    idx = 2 #start with index 2 because index 1 is reserved for *root*
    idx_dict = {} # key index value definition of the word
    word_dict = {} # key word, value all indexes of different meanings (word senses)
    for line in w2v_file:
        line = line.split(" ")
        word = line[0]
        synsets = wikiwordnet.get_synsets(word) # get different meanings of word
        if len(synsets) > 0: # if word in wordnet
            num_of_sense = 0 # initialize counter for first sense of the word
            for syn in synsets: # loop through all word senses
                for w in syn.get_words():
                    if w.lemma() == word:
                        index_file.write(str(idx) + " " + word + ' ' + str(num_of_sense) + " " + w.definition() + "\n") #create the entry in index file
                        if word not in word_dict:
                            word_dict[word] = []

                        word_dict[word].append(idx)
                        idx_dict[idx] = w.definition()
                        idx += 1
                num_of_sense += 1
    index_file.close()
    w2v_file.close()
    return word_dict, idx_dict

def find_parents(word_dict, idx_dict): #find parent for each word sense
    parent_dict = {}
    i2w = {} #key index value word.n.number_of_word_sense
    idx_file = open("idx.dat", 'r')
    for line in idx_file:
        l_array = line.split(" ")
        idx = l_array[0]
        if idx.isdigit(): #sometimes definitions of word senses more than 1 line
            word = l_array[1] #
            syn_num = l_array[2] #number of word sense (number of corresponding synset)
            i2w[int(idx)] = word + ".n." + syn_num #word unique identifier word.n.word_sense_number
            synsets = wikiwordnet.get_synsets(word)
            syn = synsets[int(syn_num)]
            children = []
            for hypernym in wikiwordnet.get_hypernyms(syn): #loop through parent synsets
                for w in hypernym.get_words(): #loop through parent words
                    parent_word = w.lemma()
                    d = w.definition() # get definition of the parent
                    if parent_word in word_dict:
                        for i in word_dict[parent_word]:
                            if idx_dict[i] == d: #get index of parent word by finding it's definition which is unique
                                parent_dict[int(idx)] = i # select one parent

    idx_file.close()
    return parent_dict, i2w

def find_children(parent_dict):
    child_dict = {}
    for i in idx_dict:
        word = i2w[i]
        child_dict[word] = [] #create array of children for each word_sense
    for par in parent_dict:
        word_idx = par
        word = i2w[word_idx]
        parent_idx = parent_dict[par]
        parent_word = i2w[parent_idx] #get parent word
        if word not in child_dict[parent_word]:
            child_dict[parent_word].append(word) #write word to the children list of it's parent
    return child_dict

def add_parent(idx): #function which returns index of the parent
    if idx in parent_dict:
        return parent_dict[idx]
    else:
        return 1

def make_catcode_file(idx_dict):
    catcode_file = open("catcode.dat", "w")
    for i in idx_dict:
        word = i2w[i]
        catcode_file.write(word) #write word to file
        idx = i
        parents = []
        while idx != 1: #recursively get parents
            p_idx = add_parent(idx)
            parents.append(p_idx)
            idx = p_idx
        parents = parents[::-1] #inverse the order from the root to leaves
        length = len(parents)
        array = [0] * (17 - length)
        parents.extend(array) #get missing zeros to get the standard 17-length format
        for p in parents:
            catcode_file.write(" " + str(p))
        catcode_file.write("\n")
    catcode_file.close()

def delete_repititions(file_name): #in wordnet some words in synset repeat, which causes duplication in file. This function deletes duplicate lines of given file
    with open(file_name, 'r') as source_file:
        lines = []
        for line in source_file:
            if line not in lines:
                lines.append(line)
        new_file = open(file_name + "_no_duplicates", 'w')
        new_file.writelines(lines)
        new_file.close()
    source_file.close()

def create_word_sense_children_file(i2w, child_dict, idx_dict, parent_dict):
    word_sense_children_file = open("children.dat", "w")
    child_dict["*root*"] = []  # add root for the correct format
    for i in idx_dict:
        if i not in parent_dict:  # word has no parent
            if i2w[i] not in child_dict["*root*"]:  # and not in the children of root yet
                child_dict["*root*"].append(i2w[i])  # add it to the children of root
    word_sense_children_file.write("*root*")
    for c in child_dict["*root*"]:
        word_sense_children_file.write(" " + c)
    word_sense_children_file.write("\n")
    for i in idx_dict:
        word = i2w[i]
        word_sense_children_file.write(word)
        for c in child_dict[word]:
            word_sense_children_file.write(" " + c)
        word_sense_children_file.write("\n")  # write children of word in one line
    word_sense_children_file.close()

if __name__ == "__main__":
    word_dict, idx_dict = create_index_file()
    parent_dict, i2w = find_parents(word_dict, idx_dict)
    child_dict = find_children(parent_dict)
    make_catcode_file(idx_dict)
    delete_repititions("catcode.dat")
    create_word_sense_children_file(i2w, child_dict, idx_dict, parent_dict)
    delete_repititions("children.dat")
