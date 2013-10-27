from collections import defaultdict
from nltk.corpus import wordnet as wn
from sets import Set
import re
import docreader

'''
Generates supervised word senses based on WordNet
'''
def get_senses(raw_queries):
  senses = defaultdict(lambda : defaultdict( lambda : defaultdict(float)))
  totals = defaultdict(lambda : defaultdict(float))
  context_words = defaultdict(Set)
  #default = 'DEFAULT'
  processor = docreader.Preprocessor()
  sense_id = 0
  
  # Need the un-processed query words!!!
  for query in raw_queries:
    line = re.sub('<.*?>|(\\n)', '', query)
    line = re.sub('[\.\',-]', ' ',line)
    q_word_list =  line.split(' ')    
    # For each word in query
    for word in q_word_list:
      word = re.sub('[^A-Za-z0-9_-]+', '', word)
      processed_q_word = processor.preprocessWord(word)
      if processed_q_word != '':
        # get synsets if possible
        syns = wn.synsets(word)
        if len(syns) >= 2:
          # For each element in the synsets (= 1 sense)
          for syn in syns:
            wordList = []
            # Get discription, pre-process and add all words to sense dict and list of contextwords
            wordList += processor.preprocessWords( syn.definition)
            # Repeat for hypernym(s)
            hypernyms = syn.hypernyms()
            for hyper in hypernyms:
              wordList += [processor.preprocessWord(hyper.lemmas[0].name)] 
              wordList += processor.preprocessWords( hyper.definition)
            # Add as word sense
            for w in wordList:
              senses[processed_q_word][sense_id][w] += 1
              totals[processed_q_word][sense_id] += 1
              context_words[processed_q_word].add(w)
            sense_id += 1
          sense_id = 0
  
  # Normalize
  for q_word, w_senses in senses.items():
    context_words[q_word] = list(context_words[q_word])
    for s_id, context in w_senses.items():
      for c_word in context.keys():
        context[c_word] = context[c_word] / totals[q_word][s_id]
  
  
  
  return (senses, context_words)
