__author__ = 'alicebenziger'

import argparse
import re
import os
import fnmatch
import string
import numpy as np
import random

# Stop word list
stopWords = ['a', 'able', 'about', 'across', 'after', 'all', 'almost', 'also',
             'am', 'among', 'an', 'and', 'any', 'are', 'as', 'at', 'be',
             'because', 'been', 'but', 'by', 'can', 'cannot', 'could',
             'did', 'do', 'does', 'either', 'else', 'ever', 'every', 'for',
             'from', 'get', 'got', 'had', 'has', 'have', 'he', 'her', 'hers',
             'him', 'his', 'how', 'however', 'i', 'if', 'in', 'into', 'is',
             'it', 'its', 'just', 'least', 'let', 'likely', 'may',
             'me', 'might', 'most', 'my', 'neither', 'no', 'nor',
             'of', 'off', 'often', 'on', 'only', 'or', 'other', 'our',
             'own', 'rather', 'said', 'say', 'says', 'she', 'should', 'since',
             'so', 'some', 'than', 'that', 'the', 'their', 'them', 'then',
             'there', 'these', 'they', 'this', 'tis', 'to', 'too', 'twas', 'us',
             've', 'was', 'we', 'were', 'what', 'when', 'where', 'which',
             'while', 'who', 'whom', 'why', 'with', 'would', 'yet',
             'you', 'your', 'mrs', 't','s']


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
    Retrieves the file content and returns
    the contents as a text string
    """
    input_file = open(filename,'r')
    text = input_file.read()
    input_file.close()
    return text


def parseFile(document):
    """
    Given a text input, the function cleans up the text
    by removing extra spaces, punctuations ,stop words etc.
    The function then splits the text into words and returns
     a list of words in the text
    """
    document = re.sub(r'[0-9+]', " ", document)
    regex = re.compile('[%s]' % re.escape(string.punctuation))
    doc = regex.sub(" ", document)
    doc = re.sub('\s+', ' ', doc).strip()
    doc.replace('\n', " ").replace('\r', " ")
    wordlist = doc.split(" ")
    wordlist = [word for word in wordlist if word not in stopWords]
    return wordlist


def updateWordCount(dic, wordlist):
    """
    Given a dictionary and list of words,
    the function updates the dictionary with
    the words in the word list as the dictionary keys and
    the corresponding word count as the dictionary values
    """

    for word in wordlist:
        if word not in dic:
            dic[word] = 0
        dic[word] += 1

def probabilityEstimator(dic,V):
    """
    The function takes in a dictionary of words, and their counts per class
    for the training set. It also takes in the number of unique words in Vocabulary.
    It then computes the P(word/Class) and returns a dictionary
    with the class, words and their probabilities.
    The dictionary returned is of the form {neg:{word1 : p(word1/neg),...},
                                            pos:{word1 : p(word1/pos),...}
    For each class I add an "UKNOWN_WORD" probability as well to account
    for words in the test set that are not in the training set
    """
    wordProbDict = {}
    total_word_count = {"pos": 0,
                        "neg": 0,
                        }
    for cl, word_count in dic.iteritems():
        for word, count in word_count.iteritems():
            total_word_count[cl] += dic[cl][word]
    for cl, word_count in dic.iteritems():
        wordProbDict[cl] = {}
        for word, count in word_count.iteritems():
            wordProbDict[cl][word] = (float(count) + 1.0)/(float(total_word_count[cl]) + float(V)+1.0)
    return wordProbDict


def splitTrainingTest(files, training_percent):
    """
    The function takes in a set of files and the percentage
    of training sets required. It returns the files divided into
    training and test documents

    """
    training_files_len = int(len(files) * training_percent)
    training_docs = []
    while len(training_docs) != training_files_len:
        index = random.randint(0, len(files)-1)
        f = files[index]
        training_docs.append(f)
        files.remove(f)
    test_docs = files
    return training_docs, test_docs


def main():
    args = parseArgument()
    directory = args['d'][0]
    accuracy = 0.0

    for i in range(0, 3):
        print "Iteration: %d" % (i+1)
        dic = {"pos": {}, "neg": {}}
        neg_files = []
        pos_files = []
        for cl in dic.keys():
            for f in os.listdir(os.path.join(directory, cl)):
                if fnmatch.fnmatch(f, '*.txt'):
                    if cl == 'pos':
                        pos_files.append(f)
                    if cl == 'neg':
                        neg_files.append(f)
        training_doc_neg, test_doc_neg = splitTrainingTest(neg_files, 0.667)
        training_doc_pos, test_doc_pos = splitTrainingTest(pos_files, 0.667)

        unique_words = set()
        # parsing every file in the training docs and creating a dictionary
        # which contains the words and word counts for each class
        # the dictionary is of the form {pos: { word1 : count(word1),...},
        #                                neg: { word1 : count(word1),...}}
        for f in training_doc_pos:
            text = getFileContent(os.path.join(directory, 'pos', f))
            word_list = parseFile(text)
            unique_words.update(word_list)
            updateWordCount(dic["pos"], word_list)


        for f in training_doc_neg:
            text = getFileContent(os.path.join(directory, 'neg', f))
            word_list = parseFile(text)
            unique_words.update(word_list)
            updateWordCount(dic["neg"], word_list)
        V = len(unique_words)

        # wordProbDict will have for every word in the training set
        # its probability given a class; P(word/Class)
        wordProbDict = probabilityEstimator(dic, V)
        total_word_count_training = {"pos": 0,
                                     "neg": 0,
                                    }
        for cl, word_count in dic.iteritems():
            for word, count in word_count.iteritems():
                total_word_count_training[cl] += dic[cl][word]


        test_docs = {
            "pos": test_doc_pos,
            "neg": test_doc_neg,
            }

        correctly_classified = {
            "pos": 0,
            "neg": 0,
            }

        for test_doc_cl, test_cl_docs in test_docs.iteritems():
            # for each file in the test document
            # the words are tokenized. The probability corresponding
            # to every word in the test file is fetched from the
            # training word probability dictionary containing P(word/class)
            # P(class/word) is computed for both the classes.
            # The class corresponding to the max log(Pc)+sum(count(word_i)*log(P(class/word_i))
            # is taken as the predicted class
            for f in test_cl_docs:
                text = getFileContent(os.path.join(directory, test_doc_cl, f))
                word_list = parseFile(text)
                word_map = {}
                updateWordCount(word_map, word_list)
                # cl_scores is a dictionary whose value
                # will be the positive and negative bayesian probability per
                # class of a word
                cl_scores = {"pos": np.log(0.5), "neg": np.log(0.5)}
                for w, c in word_map.iteritems():
                    for cl in cl_scores:
                        if w not in wordProbDict[cl]:
                            cl_scores[cl] += float(c)*np.log((float(1.0)/(float(total_word_count_training[cl])
                                                                          + float(V)+1.0)))
                        if w in wordProbDict[cl]:
                            cl_scores[cl] += float(c) * np.log(wordProbDict[cl][w]) # fetching prob from the training set per class)
                if cl_scores["pos"] > cl_scores["neg"]:
                    max_cl = "pos"
                else:
                    max_cl = "neg"

                if max_cl == test_doc_cl:
                    correctly_classified[test_doc_cl] += 1

        print "num_pos_test_docs: %s" % len(test_doc_pos)
        print "num_pos_training_docs: %s" % len(training_doc_pos)
        print "num_pos_correct_docs: %s" % correctly_classified["pos"]
        print "num_neg_test_docs: %s" % len(test_doc_neg)
        print "num_neg_training_docs: %s" % len(training_doc_neg)
        print "num_neg_correct_docs: %s" % correctly_classified["neg"]
        print "accuracy: %s" % (100 * (float(correctly_classified["pos"])
                                       + correctly_classified["neg"])/(len(test_doc_neg) + len(test_doc_pos)))
        accuracy += 100 * (float(correctly_classified["pos"])+ correctly_classified["neg"])/(len(test_doc_neg) + len(test_doc_pos))
    ave_accuracy = float(accuracy)/3.0
    print "ave_accuracy: %f" % ave_accuracy

main()
