#!/usr/bin/env python3


import sys
import re
import logging
import random
import wikipedia as wiki
import pandas as pd

from nltk import word_tokenize, sent_tokenize


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='claire.log')
question_logger = logging.getLogger('question')

wiki.set_lang("de")

class ClaireClever(object):
    def __init__(self, botname="CLaire CLever", username="User", language="de"):
        self.name = botname
        self.user_info = {"name": username}
        self.language = language
        self.history = list()
        self.expecting = False

        self.read_basic_knowledge()
        self.read_knowledge_files()
        
    def read_basic_knowledge(self):
        self.keyw = set()
        self.greetings = [("hallo",), ("hi",), ("grüezi",), ("ciao",), ("guten", "tag")]
        self.bye = [("tschüss",), ("tschau",), ("bye",), ("auf", "wiedersehen")]
        self.excuses = ["Leider verstehe ich deine Frage nicht. Versuche bitte, sie anders zu formulieren.",
            "Ich bin mir nicht sicher, ob ich dich richtig verstanden habe... Was meinst du genau?",
            "Kannst du mir weiterhelfen? Ich weiss nicht, was du genau wissen willst.",
            "Bitte formuliere deine Frage um; ich tappe gerade im Dunkeln."
            ]
        self.keyw.update(i[0] for i in self.greetings)
        self.keyw.update(i[0] for i in self.bye)                
        
    def read_knowledge_files(self):
        self.intents = dict()
        self.answers = dict()
        self.descriptions = dict()
        
        intents = pd.read_csv("intents.csv", header=None, delimiter=";", comment="%")
        for i in range (len(intents)):
            intent = intents.iloc[i, 0]
            keywords = intents.iloc[i, 1].split(",")
            for i in range (len(keywords)):
                keywords[i] = keywords[i].lower()
            self.keyw.update(keywords)
            self.intents[intent] = set(keywords)
        
        answers = pd.read_csv("answers.csv", header=None, delimiter=";", comment="%")
        for i in range (len(answers)):
            intent = answers.iloc[i, 0]
            answer = answers.iloc[i, 1]
            self.answers[intent] = answer
        
    def compute(self, input):
        question_logger.info(input)
        answer = self.interpret(input)
        if answer == "Tschüss, bis zum nächsten Mal!":
            end_conversation = "True"
        else:
            end_conversation = "False"
        return answer, end_conversation
        
    def update_history(self, keyw=None, delete_last=False):
        if keyw != None:
            self.history.append(keyw)
        elif delete_last == True:
            del self.history[-1]
                
    def interpret(self, line):
        wiki_preprocessing = self.wiki_question(line)
        if wiki_preprocessing[0] == True:
            topic = wiki_preprocessing[1]
            try:
                page = wiki.page(topic)
                content = page.content
                definition = sent_tokenize(content)[0]
                url = page.url
                answer = 'Mein Kollege Wiki Pedia meint dazu:\n"{}"\nMehr Informationen findest du unter {}'.format(definition, url)
                return answer
            except wiki.exceptions.DisambiguationError:
                return "Mein Kollege Wiki Pedia kennt dazu mehrere Konzepte. Versuche bitte genauer zu umschreiben, was du wissen willst."
        else:
            keyw = self.preprocess(line)
            if keyw == set():
                return random.choice(self.excuses)
            self.update_history(keyw)
            
            if tuple(keyw) in self.greetings:
                return "Hi! Ich weiss (fast) alles über Computerlinguistik; frag mich einfach!"
            elif tuple(keyw) in self.bye:
                return self.end()

            else:
                possible_intents = [(keywords, intent) for keywords, intent in self.intents.items()]
                intersections = list()
                for i in range (len(possible_intents)):
                    intersection = possible_intents[i][1].intersection(keyw)
                    if len(intersection) > 0:
                        intersections.append((intersection, possible_intents[i][0]))
                
                def getKey(item):
                    return(len(item[0]))            
                intersections.sort(key=getKey, reverse=True)
                candidates = list()
                current_position = 0
                max_length = len(intersections[current_position][0])    # number of keywords
                current_length = max_length
                while current_length == max_length:
                    candidates.append(intersections[current_position])
                    current_position += 1
                    try:
                        current_length = len(intersections[current_position][0])
                    except IndexError:
                        break
                
                max_length = 0      # sum of characters in all keywords
                max_indices = list()
                for i in range (len(candidates)):
                    keyword_length = len(''.join(candidates[i][0]))
                    if keyword_length >= max_length:
                        max_length = keyword_length
                        max_indices.append(i)
                
                winner = random.sample(max_indices, 1)[0]
                intent = candidates[winner][1]
                answer = self.answers[intent]
                if keyw in self.history[:-1]:
                    answer = "Ich habe dir doch bereits gesagt: " + answer
                return answer
            
    def preprocess(self, line):    
        tokens = word_tokenize(line)
        keyw = list()
        for i in range (0, len(tokens)):
            token = tokens[i]
            re.sub('W+', '', token)
            token = token.lower()
            if token in self.keyw:
                keyw.append(token)
            keyw.sort()
        return set(keyw)
    
    def wiki_question(self, line):
        tokens = word_tokenize(line)
        for i in range (len(tokens)):
            tokens[i] = tokens[i].lower()
        if (len(tokens) == 3 or len(tokens) == 4) and tokens[0] == "was" and tokens[1] == "ist":
            return True, tokens[2]
        else:
            return False, None

    def not_understood(self, keyw):
        return "Hmm, ich scheine deine Frage nicht verstanden zu haben. Kannst du sie bitte umformulieren?"
        
    def end(self):
        return "Tschüss, bis zum nächsten Mal!"
        
if __name__ == "__main__":
    claire = ClaireClever()
