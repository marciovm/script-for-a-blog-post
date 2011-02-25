#!/usr/bin/env python
# encoding: utf-8
"""
hackerswanted.py

Created by Marcio von Muhlen on 2011-01-05.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import message
import shelve

def parser(filename):
  """
  Given an ASCII file specified by filename containing sequential email messages 
  extracted from Apple Mail and separated by -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
  Parse messages and return list of message objects 
  """
  fileStream = open(filename, 'rU')
  messages = []
  bodyTxt = '' # initialize text holder
  
  for line in fileStream:
    if line[:4] == "DATE": date = line[5:]
    elif line[:4] == "SEND": pass
    elif line[:4] == "SUBJ": subject = line[7:]
    elif line[:4] == "RECI": pass
    elif line[:6] != '-*-*-*': # iterate through body lines...
      bodyTxt += line
    else: # ...until reaching end of a msg
      msg = message.Message(date, subject, bodyTxt)
      messages.append(msg)
      bodyTxt = '' # reset text holder
  fileStream.close()
  return messages

def globalWordDict(messages, length, exclusionList):
  """ 
  globalWordDict combines all the word dicts in messages and returns (word, count) tuples in sorted order
  
  messages is a list of message objects
  length determines minimum word length to include
  exclusionList is a list of strings for which the presence of any in a msg should exclude entire msg from result
  """
  result = {}
  exCount = 0
  
  for msg in messages:
    wordDict = msg.wordDict()
    if not contains(wordDict, exclusionList):
      for word in wordDict:
        if len(word) >= length:
          if result.get(word) == None:
            result[word]= wordDict[word]
          else:
            result[word]= result[word] + wordDict[word]
    else: 
      exCount += 1
  
  print 'number of msgs excluded:', exCount
  return result

def sortedDict(wordDict):
  """
  returns sorted tuple representation of (key, values) in wordDict
  ignores common words, as defined in commonWords.txt
  """
  # drop common words from count
  f = open('commonWords.txt')
  commonWords = f.read()
  commonWordsList = commonWords.split(',')
  wordTuples = []
  for key in wordDict:
    if key not in commonWordsList: 
      wordTuples.append((key, wordDict[key]))
  return sorted(wordTuples, key=tup, reverse=True)

def tup(s):
  return s[1]

def globalPhraseDict(messages, length):
  """
  combines all messages and return global phrase dict
  """
  result = {}
  for msg in messages:
    phraseDict = msg.phraseDict()
    for phrase in phraseDict:
      if len(phrase) >= length:
        if result.get(phrase) == None:
          result[phrase]= phraseDict[phrase]
        else:
          result[phrase]= result[phrase] + phraseDict[phrase]
  return result
  
def contains(wordDict, wordList):
  """ returns true if wordDict contains any of the words in wordlist"""
  for word in wordList:
    if wordDict.get(word): 
      return True
  return False

def wordListCount(wordDict, wordList):
  """ return a list of tuples with number of occurences of words in wordList in wordDict"""
  result = []
  for word in wordList:
    result.append((word, wordDict.get(word)))
  return result
  
def postAnalyzer(messageDict, negDict, posDict):
  """ analyzes a message word and phrase count by comparing against reference dicts
  messageDicts is dicts to analyze
  negDicts is dict that represent a negative score direction
  posDicts represent positive 
  """
  TOP = 10 #ignore rare words and phrases by only using TOP number ranked occurences
  msgSorted = sortedDict(messageDict)[:TOP]
  result = 0
  
  #scoring function: if top-10 word in message matches word in neg/posDicts, add score weighed by occurence in neg/posDicts AND occurence in message
  for word in msgSorted:
    if word[0] in negDict: 
      result = result - 1*messageDict[word[0]]
    if word[0] in posDict:
      result = result + 1*messageDict[word[0]]
  return result
  

def loadAltoids():
  """ load Altoids emails """
  messages = parser('batchone.txt')
  messages.extend(parser('batchtwo.txt'))
  messages.extend(parser('batchthree.txt'))
  return messages
  
def saveResults(gWords, filename):
  f = open(filename, 'w')
  for word in gWords:
    f.write(word[0] + ',' + str(word[1]) + '\n')
  f.close()

def counts(messages):
  
  #word count
  NUM = 100 #top NUM words to print
  MIN = 5 #with MIN length
  EXCLUDE = ['ta', 'lecture', 'course description', 'grad school', 'correction', 'announcement', 'websis'] #excluding messages containing any of the words in EXCLUDE
  print "\n*****PARSING*****\n"
  gWords = sortedDict(globalWordDict(messages, MIN, EXCLUDE))
  print "\ntotal messages", len(messages)
  print "\nword count"
  print gWords[:NUM]
  saveResults(gWords, 'words.csv')
  
  #phrase count
  print "\nphraseDict"
  gPhrases = sortedDict(globalPhraseDict(messages, MIN+3))
  print gPhrases[:NUM]
  saveResults(gPhrases, 'phrases.csv')


  #a priori interesting count
  print "\nprogramming language count"
  pls = ['ruby', 'rails', 'RoR', 'python', 'java', 'css', 'html', 'php', 'ajax', 'javascript', 'jquery', 'c', 'c++', 'c#', 'ios', 'iphone', 'android', 'mobile', 'web', 'net', 'asp', 'api', 'apis', 'mac', 'chrome', 'sql', 'mysql', 'unix', 'linux', 'kernel', 'database', 'hacker', 'ninja', 'guru', 'rockstar', 'ninjas', 'gurus', 'rockstars', 'hackers', 'ipad', 'startups', 'startup', 'internet', 'algorithm', 'algorithms', 'analysis', 'analyses', 'modeling', 'compilers', 'concurrent']
  print wordListCount(globalWordDict(messages, 0, EXCLUDE), pls)
  saveResults(wordListCount(globalWordDict(messages, 0, EXCLUDE), pls), 'progLang.csv')
  
  plsPhrase = ['on rails', 'objective c', 'asp net', 'social networking', 'social networks', 'social network', 'real time']
  print "\nprogramming language count from phrases"
  print wordListCount(globalPhraseDict(messages, 3), plsPhrase)
  
  #location count
  print "\nlocation count"
  places= ['boston', 'cambridge', 'francisco', 'chicago', 'nyc', 'austin', 'berkeley']
  placesPhrase = ['san francisco', 'palo alto', 'new york', 'york city', 'san diego', 'silicon valley', 'mountain view']
  print wordListCount(globalWordDict(messages, 0, EXCLUDE), places)
  print wordListCount(globalPhraseDict(messages, 3), placesPhrase)
  saveResults(wordListCount(globalWordDict(messages, 0, EXCLUDE), places), 'locations.csv')
  saveResults(wordListCount(globalPhraseDict(messages, 3), placesPhrase), 'locationsPhrase.csv')

def main():
  
  #load data
  if len(sys.argv)>1:
    d=shelve.open(sys.argv[1])
    messages = d['msgs']
  else:
    messages = loadAltoids()
    d = shelve.open('altoids.s')
    d['msgs'] = messages
    d.close()
  
  MIN = 5
  counts(messages)
  
  #like-ness
  #load 5 big co like ('BCL') and 5 yc like ('YCL') job posts.  do word/phrase count on each. 
  #BCLs: goog, msft, amzn, yhoo
  #YCL: mixpanel, dropbox, indinero, 1000memories, rapportive
  
  bigcoMsgs = parser('bigcoposts.txt')
  bigcoDict = globalWordDict(bigcoMsgs, MIN, [])
  #bigcoPhraseDict = globalPhraseDict(bigcoMsgs, MIN+3)  
  print "\nbigCo word count", sortedDict(bigcoDict)[:10]
  #print "\nbigCo phrase count", sortedDict(bigcoPhraseDict)[:10]
  
  ycMsgs = parser('ycposts.txt')
  ycDict = globalWordDict(ycMsgs, MIN, [])
  #ycPhraseDict = globalPhraseDict(ycMsgs, MIN+3)  
  print "\nYC word count", sortedDict(ycDict)[:10]  
  #print "\nYC phrase count", sortedDict(ycPhraseDict)[:10]
  
  # #combine word and phrase dicts
  #messages[0].wordDict().update(messages[0].phraseDict())
  #bigcoDict.update(bigcoPhraseDict)
  #ycDict.update(ycPhraseDict)
  
  # ycResults = []
  # for msg in ycMsgs:
  #   ycResults.append(postAnalyzer(msg.wordDict(),  bigcoDict, ycDict))
  # print "yc post analyzer", ycResults
  
  
  postAnalyzerResults = []
  for msg in messages:
    postAnalyzerResults.append((postAnalyzer(msg.wordDict(),  bigcoDict, ycDict), msg.fleschScore()))
    
  #print "post analyzer", postAnalyzerResults
  f = open('postAnalyzerResults.csv', 'w')
  for val in postAnalyzerResults:
    f.write(str(val[0]) + "," + str(val[1]) + "\n")
  f.close()
  print 'test with AKAMAI'
  msg = parser('akamai.txt')[0]
  print postAnalyzer(msg.wordDict(),  bigcoDict, ycDict), msg.fleschScore()
  
  print 'test with Opzi'
  msg = parser('opzi.txt')[0]
  print postAnalyzer(msg.wordDict(),  bigcoDict, ycDict), msg.fleschScore()
  
  print 'test with mine'
  msg = parser('mine.txt')[0]
  print postAnalyzer(msg.wordDict(),  bigcoDict, ycDict), msg.fleschScore()
  
if __name__ == '__main__':
	main()

