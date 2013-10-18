import os
import re
from collections import defaultdict
import nltk
from nltk.stem import PorterStemmer
#from nltk.stem.snowball import EnglishStemmer as SnowballStemmer


import utilities

# represents a document
class Doc(object):

   def __init__(self,docID, content, fieldValues=defaultdict(list)) :
     self.ID = docID
     self.fieldContents = fieldValues
     self.mainContent = content


# preprocesses words
class Preprocessor():
  
  def __init__(self, stopWordsFileName="stopwords.txt"):
    self.stopWordsFileName = stopWordsFileName
    self.stopwords = self.readStopWords()
    self.stemmer = PorterStemmer() # works on words
     
  def readStopWords(self):
    f = open(self.stopWordsFileName)
    lines = [line.strip() for line in f]
    f.close()
    return lines
    
  # returns a preprocessed word
  def preprocessWord(self, word):
    
    word = re.sub('[^A-Za-z0-9_-]+', '', word)
    
    if (word == ''): # word was only punctuation
      return ''
    
    word = word.lower()
    
    if  word in self.stopwords:  
      return ''
      
    word = self.stemmer.stem(word)          
    
    
    
    return word
  
  # returns preprocessed word list
  def preprocessWords(self, line):
    
    line = re.sub('<.*?>|(\\n)', '', line) # remove <></> tags and newline signs
    line = re.sub('[\.,]', ' ',line) # replace commans and dots by a space
    
    
    wordList =  line.split(' ')
    newWordList = []
    for w in wordList:
      newW = self.preprocessWord(w)
      if newW != '':
        newWordList.append(newW)
    return newWordList

# reads in documents one-by-one (see getNextDocFromFiles method)
class DocReader(object):

  startDoc = '<DOC>'
  endDoc = '</DOC>';

  startMain = '<TEXT>'
  endMain = '</TEXT>'
  
  startID = '<DOCNO>'
  endID = '</DOCNO>'
  
  fieldList = ['HEADLINE', 'BYLINE',  'SOURCE', 'FLAG', 'SECTION']


  def __init__(self, listOfFileNames, preprocessor):

    self.listOfFileNames = list(reversed(listOfFileNames))
    self.currentOpenFile = None
    self.currentOpenFileName = None
    self.docCounter = 0
    self.fileCounter = 0
    
    self.preprocessor = preprocessor 

  # this is for processing the SOURCE, HEADLINE etc. fields
  # when we know we are at the start of a document
  def processField(self, docFile, line, fieldName):
    fieldValue = []

    while True:
      oldLine = line  
      
      if line != '':
        lineList = self.preprocessor.preprocessWords(line)     
        fieldValue.extend(lineList);
      
      if '</'+fieldName+'>' in oldLine:
        return fieldValue
        
      line = docFile.readline();

  # give the current file, process a document:
  # create a Doc object
  def processDoc(self, docFile) :

    fieldValues = defaultdict(list)
    contentWords =  []
    docID = None
    
    main = False
    
    while True:
      line = docFile.readline()

      if line.startswith(DocReader.endDoc):
        return Doc(docID, contentWords, fieldValues)
        break;
      
      if line.startswith(DocReader.startID):
        docID = self.processField(docFile, line, 'DOCNO')[0]
        
      for fieldName in DocReader.fieldList:
        if line.startswith('<'+fieldName+'>'):
          fieldValue = self.processField(docFile, line, fieldName)
          fieldValues[fieldName] = fieldValue
      
      if line.startswith(DocReader.startMain):
        main = True
      elif line.startswith(DocReader.endMain):
        main = False
        
      if main:
        lineList = self.preprocessor.preprocessWords(line) 
        contentWords.extend(lineList);

  
  # get next document from the files, as a 
  # Doc object
  # returns None if the last file is empty
  def getNextDocFromFiles(self) :
    
    if self.currentOpenFile == None:
      if self.listOfFileNames == []:
        return None
      else:
        self.currentOpenFileName = self.listOfFileNames.pop()
        self.currentOpenFile = open(self.currentOpenFileName)
        print "Processing file nr. %d: %s " % (self.fileCounter, os.path.basename(self.currentOpenFileName))
        self.fileCounter += 1

    line = self.currentOpenFile.readline();

    if not line:
        self.currentOpenFile = None
        return self.getNextDocFromFiles()

    if line.startswith(DocReader.startDoc):
        #print "Processing doc nr. %d from %s" % (self.docCounter, os.path.basename(self.currentOpenFileName))
        thisDoc = self.processDoc(self.currentOpenFile)
        self.docCounter += 1
        return thisDoc



def DocReaderManager(object):
  pass



def readQueries(topicFileName) :
  topicFile = open(topicFileName)
  queryList = []
  while True:
    line = topicFile.readline()
    if not line:
      break
    if line.startswith('<EN-title>'):
      query= re.search( "<EN-title>(.*?)</EN-title>" , line ).group(1)
      query = query.strip()
      queryList.append(query)
  
  return queryList
  
def queriesToTermList(queryList) :
  wordList = []
  preprocessor = Preprocessor()
  
  for query in queryList:
    queryNewList = preprocessor.preprocessWords(query)
    wordList.extend(queryNewList)
  
  return wordList


# TODO: deel filenames door nr_processors
# maak ook threaded
def run() :
  docFileNames  = getFileNames("/run/media/root/ss-ntfs/3.Documents/huiswerk_20132014/CS&P/project/data1/docs")

  pp = Preprocessor("stopwords.txt")
  dr = DocReader(docFileNames, pp)

  #169 478 docs
  
  number = 10
  d =  'meaningless init value'
  while d != None and number > 0:
    d =  dr.getNextDocFromFiles()
    number -= 1
    #print getDictString(d.fieldContents)
    #print d.mainContentnt
    print d.ID
  print dr.docCounter
  
  
  queries = readQueries("/run/media/root/ss-ntfs/3.Documents/huiswerk_20132014/CS&P/project/data1/original_topics.txt")
  queryWords = queriesToTermList(queries)
  
  print queryWords

if __name__ == '__main__': #if this file is the argument to python
  run()
