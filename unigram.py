import argparse
import re
import os
import fnmatch
import csv



# Stop word list
stopWords = ['a', 'able', 'about', 'across', 'after', 'all', 'almost', 'also',
             'am', 'among', 'an', 'and', 'any', 'are', 'as', 'at', 'be',
             'because', 'been', 'but', 'by', 'can', 'cannot', 'could', 'dear',
             'did', 'do', 'does', 'either', 'else', 'ever', 'every', 'for',
             'from', 'get', 'got', 'had', 'has', 'have', 'he', 'her', 'hers',
             'him', 'his', 'how', 'however', 'i', 'if', 'in', 'into', 'is',
             'it', 'its', 'just', 'least', 'let', 'like', 'likely', 'may',
             'me', 'might', 'most', 'must', 'my', 'neither', 'no', 'nor',
             'not', 'of', 'off', 'often', 'on', 'only', 'or', 'other', 'our',
             'own', 'rather', 'said', 'say', 'says', 'she', 'should', 'since',
             'so', 'some', 'than', 'that', 'the', 'their', 'them', 'then',
             'there', 'these', 'they', 'this', 'tis', 'to', 'too', 'twas', 'us',
             've', 'wants', 'was', 'we', 'were', 'what', 'when', 'where', 'which',
             'while', 'who', 'whom', 'why', 'will', 'with', 'would', 'yet',
             'you', 'your', 'hi', 'hey']


def parseArgument():
    """
    Code for parsing arguments
    """
    parser = argparse.ArgumentParser(description='Parsing a file.')
    parser.add_argument('-d', nargs=1, required=True)
    args = vars(parser.parse_args())
    return args


def getFileContent(filename):
    """
    retrieve file content
    """
    input_file = open(filename,'r')
    text = input_file.read()
    input_file.close()
    return text


def parseFile(dic, text, cl):
    """
    Updates the dictionary after filtering the text for stopwords
    """
    # removing all non alphanumeric characters like .'s and !'s
    data = re.sub(r'[\W]', " ", text)

    # removing all numbers
    data = re.sub(r'[0-9+]', " ", data)

    # Porter's algorithm
    # removing all sses -> ss
    data = re.sub(r' *sses', 'ss', data)

    # removing all plural like cars become car
    # but maintaining ss i.e caress remains caress
    data = re.sub(r' *([^s])s\b', r'\1',data)
    data = re.sub( '\s+', ' ', data).strip()
    tokens = data.split(" ")

    # filtering for stopwords
    tokens = [x for x in tokens if x not in stopWords]

    # calculate word counts
    for token in tokens:
        if token in dic[cl]:
            dic[cl][token] += 1
        else:
            dic[cl][token] = 1

    return dic


def writeOutput(dic, output_filename):
    """
    Output file
    """

    totals = {}
    unique_words = set()

    # Calculate sum by class and get unique words
    for cl, word_counts in dic.iteritems():
        for word,count in word_counts.iteritems():
            if cl not in totals:
                totals[cl] = 0
            totals[cl] += count
            unique_words.add(word)

    lines = []
    for word in unique_words:
        for cl, word_counts in dic.iteritems():
            if word in word_counts:
                lines.append([cl, word, word_counts[word], float(word_counts[word])/float(totals[cl])])

    with open(output_filename, 'wb') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)

        csv_writer.writerow(['class', 'word', 'count', 'probability'])
        for line in lines:
            csv_writer.writerow(line)


def main():
    args = parseArgument()
    directory = args['d'][0]
    dic = {"pos": {}, "neg": {}}

    for cl in dic.keys():
        for f in os.listdir(os.path.join(directory, cl)):
            if fnmatch.fnmatch(f, '*.txt'):
                text = getFileContent(os.path.join(directory, cl, f))
                dic = parseFile(dic, text, cl)

    writeOutput(dic, "movie_unigram.csv")

main()
