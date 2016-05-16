# coding=UTF-8
from collections import OrderedDict
from alphabet_detector import AlphabetDetector
from gensim import corpora, models, similarities, utils, matutils
from gensim.models import word2vec
import re
import os
import sys  
import hanzidentifier
import pickle

class LangId:     
  def __init__(self):
    modelPath = os.path.dirname(os.path.abspath(__file__))+'/model'
    if modelPath.endswith('/'):
      modelPath = modelPath[:-1]
    self.modelPath = modelPath
    self.initVars()
    self.SWinitVars(modelPath+'/stopwords/')

  def SWinitVars(self, mypath):
    self.SWlangIds = []
    self.SWvecs = {}
    self.SWmodel = {}
    if mypath.endswith('/'):
      mypath = mypath[:-1]
    for filename in os.listdir(mypath):
      self.SWvecs[filename] = vec(mypath+"/"+str(filename))
      self.SWmodel[filename] = word2vec.Word2Vec(self.SWvecs[filename].ss, size=2, min_count=1)

  def initVars(self):
    reload(sys)  
    sys.setdefaultencoding('utf8')
    f = open(self.modelPath+'/languages', 'r')
    self.languages = f.read().split('\n')
    self.languages.pop()  
    print 'self.modelPath+/corpus.mm',self.modelPath+'/corpus.mm'
    if os.path.exists(self.modelPath+'/corpus.mm'):
      self.dictionary = corpora.Dictionary.load(self.modelPath+'/dict.dict')
      self.corpus = corpora.MmCorpus(self.modelPath+'/corpus.mm')
      self.tfidf = models.TfidfModel.load(self.modelPath+'/model.tfidf')
      self.documents = pickle.load(open(self.modelPath+'/documents.obj', "rb" ) )
      self.texts = []
      for document in self.documents:
          self.texts.append(document) #.lower().split())   

    else:
      self.documents = []
      for lang in self.languages:
        self.documents.append(self.readFile(self.modelPath+'/'+lang.lower()))
      self.texts = []
      for document in self.documents:
          self.texts.append(document) #.lower().split())   
      self.newModelFiles()

  def newModelFiles(self):     
    self.dictionary = corpora.Dictionary(self.texts)
    self.corpus = [self.dictionary.doc2bow(text) for text in self.texts]
    self.dictionary.save(self.modelPath+'/dict.dict')
    self.tfidf = models.TfidfModel(self.corpus) # step 1 -- initialize a model
    self.tfidf.save(self.modelPath+'/model.tfidf') # same for tfidf, lda, ...
    pickle.dump(self.documents, open(self.modelPath+'/documents.obj', "wb" ) )
    corpora.MmCorpus.serialize(self.modelPath+'/corpus.mm', self.corpus)

  def SWsimilar(self,model,v,txt):
    doc_tokens = txt.lower().split()
    w = filter(lambda x: x in v.ss2, doc_tokens)
    dif = len(doc_tokens) - len(w)  
    ##print "===",w,dif,len(doc_tokens) , len(w) ,v.ss2
    if len(w) > 0:
      try:
        return model.n_similarity(v.ss2, w) - dif
      except Exception, e:
        return dif * -1
    else:
      return dif * -1

  def SWdetect_language(self,text):
    sim = []
    n = 0
    for item in self.SWmodel:
      ##print item
      sim = self.SWsimilar(self.SWmodel[item],self.SWvecs[item],text)
      ##print sim
      if (n == 0) or (n < sim):
        lang = item
        n = sim
    if (n == (len(text.lower().split()) * -1)):
      return ""
    else:
      return lang      

  def sim_tfidf(self, doc):     
      try:
        vec_bow = self.dictionary.doc2bow(doc)#.lower().split())
        vec_tfidf = self.tfidf[vec_bow] # convert the query to LSI space
        index = similarities.MatrixSimilarity(self.tfidf[self.corpus])
        sims = index[vec_tfidf]
        return sorted(enumerate(sims), key=lambda item: -item[1])
      except ValueError:
        return []

  def threeGrams(self,b):
    n = 3
    ret = []
    for i in range(0, len(b), 1):
      ret.append(b[i:i+n])
    return ret

  def normalize(self,text): 
      """normalization for twitter"""
      text = text.lower()
      text = filter(lambda c: not c.isdigit(), text)
      text = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', text) #url
      text = re.sub(r"(?:\@|\#)\S+", "", text) #@user #hashtag
      text = re.sub(r'(^| )[:;x]-?[\(\)dop]($| )', ' ', text)  # facemark
      text = re.sub(r'(^| )(rt[ :]+)*', ' ', text)
      text = re.sub(r'([hj])+([aieo])+(\1+\2+){1,}', r'\1\2\1\2', text, re.IGNORECASE)  # laugh
      text = re.sub(r' +(via|live on) *$', '', text)
      text = re.sub('«»“”"[.,!%@#$<>:;}?{()+-=-_&*@|\/"]+', ' ', text)
      text = re.sub('(\!|#|\*|\?|,|;|:|%|\$|\"|\.\.\.)', ' ', text)
      text = re.sub('  +', ' ', text)
      text = re.sub('hahaha', '', text)
      text = re.sub('haha', '', text)
      text = re.sub('(\sx\s|\sX\s)+', ' ', text)
      text = re.sub('(\👌|\€|\😪|\❤️|\😌|\✨|\➡|\⬅|\☕️|\😂|\😃|\😎|\😁|\😢|\😉|\😴|\😊|\♡|\😚|\😘|\😍|\💕|\💓|\💙|\💛|\💖|\💜|\💞|\🎉|\💗|\🔛)+', '', text)
      text = re.sub('(؟|\/|\t|\n+| - |\.)', ' ', text)
      text = re.sub(r'\\', ' ', text)
      text = re.sub('\|', '', text)
      text = re.sub('\[', '', text)
      text = re.sub('\]', '', text)
      text = re.sub('\(', '', text)
      text = re.sub('\)', '', text)
      text = re.sub('(  )+', ' ', text)
      while text.startswith(' '):
        text = text[1:]
      while text.endswith(' ') or text.endswith('\n'):
        text = text[:-1]
      return text

  def readFile(self,filesPath):
    i = []# u''
    for file in os.listdir(filesPath):
      if file.endswith(".txt"):
        fd = open(filesPath+'/'+file, 'r')
        for line in fd.readlines():
          try:
            s = self.threeGrams(self.normalize(unicode(line)))
            #if re.match("", s):
            i = i+s
          except ValueError:
            i = i
        fd.close()
    return i  

  def classifyPerLanguage(self,line):
     text = self.normalize(unicode(line))
     ret = []
     langPreDefined = ''
     if hanzidentifier.has_chinese(text): #chinese
       chineseArray = re.findall(ur'[\u4e00-\u9fff]+',text)
       chineseChars = len(str(chineseArray)) - (2+len(chineseArray))
       if len(text) / 3 < chineseChars: #At least 1/3 of the sentence in Chinese characteres
         if hanzidentifier.identify(text) is hanzidentifier.SIMPLIFIED:
           ret = [[1,'ZH-CHS']]
         elif hanzidentifier.identify(text) is hanzidentifier.TRADITIONAL:
           ret = [[1,'ZH-CHT']]
         elif hanzidentifier.identify(text) is hanzidentifier.BOTH:
           ret = [[1,'ZH-CHT'],[1,'ZH-CHS']]
     #not chinese    
     if len(ret) == 0:
       sims = self.sim_tfidf(self.threeGrams(text))
       #print '......',text,sims
       if len(sims) > 0:
        if len(sims) > 3:
          if (sims[0][1] > 0.12) and ((sims[0][1] - sims[3][1]) < 0.036): #UNKNOWN
            return []
        language = ''
        dLanguages = {}
        for s in sims:
          if s[1] > 0:
            dLanguages[self.languages[s[0]].lower()] = s[1]
        lang1= self.languages[sims[0][0]].lower()
        lang2= self.languages[sims[1][0]].lower()
        lang3= self.languages[sims[2][0]].lower()
        print '......',text,sims,lang1,lang2,lang3,((sims[0][1] - sims[1][1]) > 0.003) , (sims[0][1] > 0.004),( ((sims[0][1] - sims[1][1]) > 0.003) and (sims[0][1] > 0.004) ) or (self.arabicAndfarsi(lang1, lang2, text))
        language = self.languageRules(lang1, lang2, lang3, dLanguages, text)
        if len(language) > 0 and (language in [lang2,lang1,lang3]):
          ret.append([1, str(language.upper())])
          langPreDefined = language.upper()
        for s in sims:
          if (self.languages[s[0]] != langPreDefined):
            ret.append( [ str(s[1]), str(self.languages[s[0]])])
     return ret

  def arabicAndfarsi(self, lang1, lang2, text):
    if ((lang2 == 'ar')  and  (lang1 == 'fa') ) or ((lang1 == 'ar')  and  (lang2 == 'fa') ):     
      return True
    else:
      return False

  def findInText(self, chars, text):
    for ch in chars:
      if text.find(ch) > -1:
        return True
    return False

  def find_words(self, text, search):
    """Find exact words"""
    dText   = text.split()
    dSearch = search.split()
    found_word = 0
    for text_word in dText:
        for search_word in dSearch:
            if search_word == text_word:
                found_word += 1
    if found_word >= len(dSearch):
        return True
    else:
        return False

  def compareLangs(self, vTarget, vLangs, vExpr, text):
    ok = True    
    n = 0
    language = ''
    for l in vLangs:
      if not (l in vTarget):
        ok = False
    if ok:
      for l in vExpr:
        for w in l:
          if (self.find_words(text, w)):
            language = vTarget[n]  
        n = n + 1
    return language

  def languageRules(self, lang1, lang2, lang3, dLanguages, text):
    language = ''
    if 'tl' in dLanguages.keys():
      if (text.find('ggong') > -1) or (text.find(' ang ') > -1) or (text.find('oong') > -1) or (text.find(' pa ') > -1):
        language = 'tl'  
      if ( text.find(' na ') > -1) and ((lang1 != 'pt')  and  (lang2 != 'pt') ):
        language = 'tl'
      if ((lang2 != 'es')  and  (lang2 != 'fr')  and  (lang1 == 'tl') ) or ((lang1 != 'es')  and (lang1 != 'fr')  and  (lang2 == 'tl') ):     
        if (self.find_words(text, 'tayo')) or (text.find(' ni ') > -1) :
           language = 'tl' 
    language = self.compareLangs(['pt', 'es','it'], [lang1, lang2, lang3], [['você'], ['nuevo'],[]], text)
    if len(language)>0:
      return language
    language = self.compareLangs(['en', 'pt', 'es'], [lang1, lang2, lang3], [['yes','day','you','this','is','access'], ['você'], []], text)
    if len(language)>0:
      return language
    language = self.compareLangs(['en', 'fr', 'es'], [lang1, lang2, lang3], [['yes','day','you','this','is','access'], [], []], text)
    if len(language)>0:
      return language
    language = self.compareLangs(['en', 'it', 'fr'], [lang1, lang2, lang3], [['yes','day','you','this','is','access'], [], []], text)
    if len(language)>0:
      return language
    if ((lang1 == 'id')  and  (lang2 == 'tr') )  or  ((lang2 == 'id')  and  (lang1 == 'tr') ) :     
      if text.find('ş') > -1:
        language = 'tr'
    elif ((lang2 == 'id')  and  (lang1 == 'tl') ) or ((lang1 == 'id')  and  (lang2 == 'tl') ):     
      if  (self.find_words(text, 'ba')) or (self.find_words(text, 'sa')) or (self.find_words(text, 'daw')) or (text.find('nasa') > -1) or (text.find(' at ') > -1)  or (text.find(' na ') > -1)  or (text.find('sila ') > -1) or (self.find_words(text, 'ka')):
         language = 'tl' 
      else:
         language = self.SWdetect_language(text)         
         if not( language in ['tl','id'] ):
            language = ''
    elif ((lang1 == 'tr')  and  (lang2 == 'az') ):     
      if text.find('ə') > -1:
         language = 'az'
    elif ((lang2 == 'ar')  and  (lang1 == 'fa') ) or ((lang1 == 'ar')  and  (lang2 == 'fa') ):     
      if self.findInText(['ﻩو','ة','دو'], text) or (self.find_words(text, 'سعيد')) or (self.find_words(text, 'حط')) :
        language = 'ar'
      elif self.findInText(['دوازده','وﻩ','پ','چ','ژ','گ'], text):       
        language = 'fa'  
    elif ((lang2 == 'en')  and  (lang1 == 'az') ) or ((lang1 == 'en')  and  (lang2 == 'az') ):     
      if (text.find('ç') > -1) or  (text.find('ə') > -1) or (text.find('ş') > -1):
         language = 'az'
      elif (text.find(' to ') > -1) or (text.find(' day ') > -1) or (text.find(' one ') > -1):
         language = 'en'  
    elif ((lang2 == 'en')  and  (lang1 == 'id') ) or ((lang1 == 'en')  and  (lang2 == 'id') ):     
      if (self.find_words(text, 'day')) or (text.find("i'm") > -1) or (self.find_words(text, 'for')) or  (text.find('thy') > -1) or (text.find('ts') > -1) or (text.find(' my ') > -1) or (text.find(' are ') > -1) or (text.find("aren't") > -1):
         language = 'en' 
    elif ((lang2 == 'en')  and  (lang1 == 'pt') ) or ((lang1 == 'en')  and  (lang2 == 'pt') ):     
      if (text.find('you') > -1) or self.find_words(text, 'is') :
         language = 'en' 
    elif ((lang2 == 'fr')  and  (lang1 == 'es') ) or ((lang1 == 'fr')  and  (lang2 == 'es') ):     
      if (text.find('dades ') > -1) :
         language = 'es' 
    elif ((lang2 == 'fr')  and  (lang1 == 'pt') ) or ((lang1 == 'fr')  and  (lang2 == 'pt') ):     
      if (text.find('dades ') > -1) :
         language = 'pt' 
    elif ((lang2 == 'pt')  and  (lang1 == 'es') ) or ((lang1 == 'pt')  and  (lang2 == 'es') ):     
      if (self.find_words(text, 'lá')) or (self.find_words(text, '(sel')) or self.find_words(text, 'lua') or (self.find_words(text, 'ali')):
         language = 'pt' 
      if (self.find_words(text, 'y')) or (self.find_words(text, 'has')) or (self.find_words(text, 'del')):
         language = 'es' 
    elif ((lang2 == 'en')  and  (lang1 == 'es') ) or ((lang1 == 'en')  and  (lang2 == 'es') ):     
      if (text.find('lly') > -1) or (text.find('you') > -1) or (text.find(' st') > -1) or (self.find_words(text, 'him'))  or (self.find_words(text, 'the')):
         language = 'en' 
      elif (text.find('leer') > -1):
         language = 'es' 
    elif ((lang2 == 'en')  and  (lang1 == 'tl') ) or ((lang1 == 'en')  and  (lang2 == 'tl') ):     
      if (text.find('easy') > -1) or (text.find('by ') > -1) or (self.find_words(text, 'i')) or (self.find_words(text, 'for')) or (self.find_words(text, 'the')):
         language = 'en' 
      elif (self.find_words(text, 'ka')):
         language = 'tl' 
    elif ((lang2 == 'en')  and  (lang1 == 'fr') ) or ((lang1 == 'en')  and  (lang2 == 'fr') ):     
      if (self.find_words(text, 'my')) or (self.find_words(text, 'yes')) or (self.find_words(text, 'be')) or (self.find_words(text, 'this')) or (self.find_words(text, 'for')) or  (text.find(' you ') > -1) or (text.find(' our ') > -1) or (text.find('will') > -1) or (text.find(' one') > -1) or (text.find('ee') > -1) :
         language = 'en' 
      elif (text.find('è') > -1):
         language = 'fr' 
      else:
         language = self.SWdetect_language(text)
    elif ((lang2 == 'en')  and  (lang1 == 'it') ) or ((lang1 == 'en')  and  (lang2 == 'it') ):   
      if (text.find('ey') > -1) or (text.find('thy') > -1) or (self.find_words(text, 'for'))  or (self.find_words(text, 'have')) or (self.find_words(text, 'to')) or (self.find_words(text, 'i')) or (self.find_words(text, 'never')) or (text.find('well') > -1) or (text.find('ts') > -1) or (text.find('ing ') > -1) or (text.find(' of ') > -1):
         language = 'en' 
      if (text.find('è') > -1):
         language = 'it' 
    elif ((lang1 == 'es')  and  (lang2 == 'en') ):     
      if (text.find('my') > -1) or (text.find('ck') > -1) or (self.find_words(text, 'i')) or (self.find_words(text, 'never')):
         language = 'en' 
    elif ((lang1 == 'it')  and  (lang2 == 'es') ):     
      if (text.find('nn') > -1) or (text.find('à') > -1)  or (text.find('ù') > -1):
         language = 'it' 
      elif (text.find('ñ') > -1) or (text.find(' ni ') > -1):
         language = 'es'
      else:
         language = self.SWdetect_language(text)
    elif ((lang1 == 'pt')  and  (lang2 == 'es') ) or ((lang2 == 'pt')  and  (lang1 == 'es') ): 
      if (text.find('ñ') > -1) or (text.find('ll') > -1) or (text.find(' y ') > -1)  or (text.find(' el ') > -1)  or (text.find(' hay') > -1):
         language = 'es'
      elif (text.find('ç') > -1) or (text.find(' e ') > -1)  or (text.find('à') > -1):
         language = 'pt'
      else:
         language = self.SWdetect_language(text)

    return language

  def add_sample(self, sentence, lang):
    try:
      idx = self.languages.index(lang)
      self.documents[idx] = self.documents[idx]  + self.threeGrams(self.normalize(unicode(sentence)))
      self.newModelFiles()
      return True      
    except ValueError:
      return False

  def list_languages(self):
    return self.languages

  def difFirstSecond(self,res):
    if (float(res[0][0]) < 1) and (float(res[0][0]) > 0) and (float(res[1][0]) > float(res[0][0]) / 3):
      return True
    else:
      return False

  def sameAlphabet(self,vLine):
    ad = AlphabetDetector()
    if len (ad.detect_alphabet(vLine.decode('utf-8'))) <= 1:
      return True
    else:
      return False

  def canBeEnglish(self,res,window):
    if window == 3 :
      if ((res[0][1].upper() == 'EN') and (float(res[0][0]) > 0)) or ((res[1][1].upper() == 'EN') and (float(res[1][0]) > 0)) or ((res[2][1].upper() == 'EN') and (float(res[2][0]) > 0)): #one of the first three languages is English
        return True
    elif window == 4 :
      if ((res[0][1].upper() == 'EN') and (float(res[0][0]) > 0)) or ((res[1][1].upper() == 'EN') and (float(res[1][0]) > 0)) or ((res[2][1].upper() == 'EN') and (float(res[2][0]) > 0))  or ((res[3][1].upper() == 'EN') and (float(res[3][0]) > 0)): #one of the first three languages is English
        return True
    return False

  def classify(self,line):  
    if len(line) > 1:
	    res = self.classifyPerLanguage(line)
	    resOriginal = res 
	    print 'line,res -><',line,res
	    if len(res) > 2: 
	      if  (not self.sameAlphabet(line)) or ( self.difFirstSecond(res) and self.canBeEnglish(res,3) )  :
		#keep first 3 languages that are not English
		first3 = []
		for x in range(0, 4):
		    first3.append(res[x][1])
		dLangs = {}
		vLine = line.split(' ')
		while len(vLine[0]) < 1:
		  vLine.pop(0)
		n = 0
		vLangs = []
		while len(vLine) > 3:
		  while len(vLine[0]) < 1:
		    vLine.pop(0)
		  w1 = vLine[0]+' '+vLine[1]+ ' '+vLine[2]
		  if (self.sameAlphabet(w1)):
		    lang = self.classifyPerLanguage(w1)
		    if len(lang) > 0 :
		      lang[0][1] = self.areEnID(lang)
		      vLangs.append([w1,lang])
		      if (lang[0][1] in first3):
		        if lang[0][1] in dLangs:
		          dLangs[lang[0][1]] += 1
		        else:
		          dLangs[lang[0][1]] = 1
		  vLine.pop(0)
		if len(vLine) > 0:
		  w1 = ''
		  for w in vLine:
		    w1 = w1+' '+w
		  if len(w1) > 2 and (self.sameAlphabet(w1)):  
		    w1 = w1[1:] #remove first char
		    lang = self.classifyPerLanguage(w1)
		    if len(lang) > 0 :
		      lang[0][1] = self.areEnID(lang)
		      vLangs.append([w1,lang])
		      if (lang[0][1] in first3):
		        if lang[0][1] in dLangs:
		          dLangs[lang[0][1]] += 1
		        else:
		          dLangs[lang[0][1]] = 1
		  res = []
		for key, value in dLangs.iteritems():
		  res.append([value,key])
		print '-->dLangs',dLangs  
		if ('EN' in dLangs) and (len(dLangs)>1) and not(len(dLangs) == 2 and 'FR' in dLangs.keys() and dLangs['FR'] == 1) :
		  return  sorted(self.formatRet2(self.formatRet1(self.percentageResult(res))).items(), key=lambda item: -item[1])
		else:
		  return sorted(self.formatRet1(self.percentageResult(resOriginal)).items(), key=lambda item: -item[1]) 
	    if len(res) >  0 and float(res[0][0]) > 0:
	      return sorted(self.formatRet1(self.percentageResult(res)).items(), key=lambda item: -item[1]) 
	    else:
	      return []
    else:
      return []
	
  def areEnID(self,lang):
    #[are] in id and en
    if lang[0][1] == 'ID' and lang[1][1] == 'EN':
      if ' are ' or "aren't" in w1:
        return 'EN'
    return (lang[0][1])

  def formatRet1(self,ret):
    retDict = {}
    for r in ret:   
      retDict[r[1]] = r[0]
    return retDict

  def formatRet2(self,retDict1):
    retDict2 = {}
    for key, value in retDict1.iteritems():
      if key != 'EN':
        retDict2['[EN,'+str(key)+']'] = value + retDict1['EN']
    return retDict2

  def percentageResult (self,res):
    totalSum = 0
    n = 0
    for r in res:
      totalSum = totalSum + float(r[0]) 
    for r in res:
      res[n][0] = float(r[0]) / float(totalSum)
      n = n + 1
    return (res)

class vec:
  def __init__(self, fi):
    self.ss = []
    self.ss2=[]
    for line in open(fi):
      self.ss.append([line.replace("\n", "").lower()])
      self.ss2.append(line.replace("\n", "").lower())

if __name__ == '__main__':
  l = LangId()
  if True: #False: #
    line = l.normalize("x")
    result = l.classify(line)
    print '***->',str(line),result
  