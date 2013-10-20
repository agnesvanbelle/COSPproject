import os
import re
from collections import defaultdict
import nltk
from nltk.stem import PorterStemmer
#from nltk.stem.snowball import EnglishStemmer as SnowballStemmer
import threading
import time
import multiprocessing
import cPickle as pickle

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
class DocReader(threading.Thread):

  startDoc = '<DOC>'
  endDoc = '</DOC>';

  startMain = '<TEXT>'
  endMain = '</TEXT>'
  
  startID = '<DOCNO>'
  endID = '</DOCNO>'
  
  fieldList = ['HEADLINE', 'BYLINE',  'SOURCE', 'FLAG', 'SECTION']

  docCounter = 0
  fileCounter = 0
    
  def __init__(self, listOfFileNames, preprocessor):

    threading.Thread.__init__(self)
    
    self.listOfFileNames = list(reversed(listOfFileNames))
    self.currentOpenFile = None
    self.currentOpenFileName = None
    
    
    self.preprocessor = preprocessor 
    
    self.docList = []
    
  def run(self):
    d =  'meaningless init value'
    
    while d != None :
      d =  self.getNextDocFromFiles()
      if d != None:
        #print getDictString(d.fieldContents)
        #print d.mainContentnt
        #print d.ID
        self.docList.append(d)
      
    
  
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
        print "Processing file (nr. ~ %d) : %s " % (DocReader.fileCounter, os.path.basename(self.currentOpenFileName))
        DocReader.fileCounter += 1

    line = self.currentOpenFile.readline();

    if not line:
        self.currentOpenFile = None
        return self.getNextDocFromFiles()

    if line.startswith(DocReader.startDoc):
        #print "Processing doc nr. %d from %s" % (DocReader.docCounter, os.path.basename(self.currentOpenFileName))
        thisDoc = self.processDoc(self.currentOpenFile)
        DocReader.docCounter += 1
        return thisDoc



class DocReaderManager(object):
  
  
  def __init__(self, fileNameList, preprocessorStopwordsFile="stopwords.txt"):
    self.fileNameList = fileNameList
    self.preprocessorStopwordsFile = preprocessorStopwordsFile
    
    self.docList = []
    
  def parseDocs(self):
    self.nrProcessors = multiprocessing.cpu_count()
    nrFiles = len(self.fileNameList)
    
    self.nrThreads  = min(self.nrProcessors, nrFiles)
    self.threads = [None]*self.nrThreads
    
    
    start = 0
    interval = nrFiles / self.nrThreads
    end = start + interval

    print "Start reading. Using %d threads." % self.nrThreads
    
    for i in range(0, self.nrThreads) :
      if (i == (self.nrThreads-1)):
        end = nrFiles

      filesSubset = self.fileNameList[start:end+1]

      print "start:%d, end:%d, filesSubset: %s " % (start, end, filesSubset)
      
      self.threads[i] = DocReader( filesSubset , Preprocessor(self.preprocessorStopwordsFile))

      start = end + 1
      end = end + interval 

    for t in self.threads:
      t.start()

    for t in self.threads:
      t.join()

    print "Done reading."

    for t in self.threads:
      
      self.docList.extend(t.docList)
      

  def getDocs(self, fromFile=False):
    if fromFile:
      self.loadDocs()
  
    else:
      self.parseDocs()
    
    return self.docList
      
  def saveDocs(self):
    if self.docList == []:
      self.parseDocs()
      
    print "Saving docs."
    file1 = open( "alldocs.dat", "wb" )
    pickle.dump( self.docList, file1, -1  )
    file1.close()

  def loadDocs(self):
    print "Loading saved docs."
    f1 = open( "alldocs.dat", "rb" ) 
    docList = pickle.load( f1 )
    self.docList = docList
    f1.close()
    
    

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


def run() :
  docFileNames  = utilities.getFileNames("Data_dummy/collection2")


  dr = DocReaderManager(docFileNames, "stopwords.txt")

  #169 478 docs
  
  print docFileNames
  
  dr.getDocs(True)
  
  queries = readQueries("Data_dummy/original_topics.txt")
  queryWords = queriesToTermList(queries)
  
  print queryWords
  
  
if __name__ == '__main__': #if this file is the argument to python
  run()
