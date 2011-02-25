import string
import flesch

class Message(object):
  """an email message object
  fields: date, subject, bodyTxt
  methods: wordCount, wordDict, readability, phraseCount
  """
  
  def __init__(self, date, subject, bodyTxt):
    self.date = date
    self.subject = subject
    self.bodyTxt = bodyTxt
    
  def printargs(self):
    """ print this message"""
    print "**Date**", self.date
    print "**Subject**", self.subject
    print "**Body**", self.bodyTxt
    
  def wordCount(self):
    """ return the number of words in this message's bodyTxt"""
    words = self.bodyTxt.split()
    return len(words)
    
  def wordDict(self):
    """ return a dict with {word, #occurences} """
    wordDict = {}
    words = self.bodyTxt.split()
    for rawWords in words:
      word = rawWords.lower().translate(string.maketrans("",""), '!"$%&\'()*,-./:;<=>?@[\\]^_{|}~') #drop these punctuation symbols
      if word:
        if wordDict.get(word) == None:
          wordDict[word]=1
        else:
          wordDict[word]=wordDict[word]+1
    return wordDict
  
  def phraseDict(self):
    """ return a dict with {word1_word2, #occurences} representing histogram of 2 word phrases"""
    phraseDict = {}
    words = self.bodyTxt.split()
    for ind in range(1,len(words)):
      phrase = (words[ind-1]+" "+words[ind]).lower().translate(string.maketrans("",""), '!"$%&\'()*,-./:;<=>?@[\\]^_{|}~')
      if phraseDict.get(phrase) == None:
        phraseDict[phrase]=1
      else:
        phraseDict[phrase]=phraseDict[phrase]+1
    return phraseDict
    
  def fleschScore(self):
    return round(flesch.summarize(self.bodyTxt)*100)/100