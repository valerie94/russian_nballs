'''This .py program converts initial file with word2vec features to standard format such as
word_1 feature1 feature2 ... feature256 /n '''
'''This script creates file ru_w2v.txt which is w2v file which is required for constracting nballs '''
import re
def change_format(file_name):#input is the initial file
    line_array = []
    intial_file = open(file_name)
    for line in intial_file:
        #replace all special symbols and split by separator
        if ("[" in line):
            line = line.replace('\t', ' ')
            line = line.replace('\n', '')
            line = re.sub('\t', ' ', line)
            line = line.replace('[', '')
            line = line.split(" ")
            line.pop(0)
            line = list(filter(None, line))
            for x in line:
                line_array.append(x)
                line_array.append(' ')
        elif ("]" in line):
            line = line.replace('\t', ' ')
            line = line.replace(']', '')
            line = line.split(" ")
            line = list(filter(None, line))
            for x in line:
                line_array.append(x)
                if ("\n" not in x):
                    line_array.append(' ')
        else:
            line = line.replace('\n', '')
            line = line.split(" ")
            line = list(filter(None, line))
            for x in line:
                line_array.append(x)
                line_array.append(" ")
    intial_file.close()
    return line_array

def write_to_output_file(lines, file_name): #write to the output file
    with open(file_name, "w") as file:
        file.write("".join(lines))
    file.close()

if __name__ == "__main__":
    w2v_file = "ru.tsv" # initial source file from https://github.com/Kyubyong/wordvectors, put this file in the project directory or specify the path
    output_w2v_file = "ru_w2v.txt" #the name of output file with w2v features
    formatted_line = change_format(w2v_file)
    write_to_output_file(formatted_line, output_w2v_file)