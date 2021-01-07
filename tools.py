import json


def stopwords(tag):
	stop_words=[]
	with open('intents.json') as file:
		intents = json.load(file)
	for i in intents["intents"]:
		if i["tag"] == tag:
			for j in i["patterns"]:
				for k in j.split(" "):
					stop_words.append(k.lower())
	stop_words = list(set(stop_words))
	
	return stop_words


def clean(text,tag):
	stop_words = stopwords(tag)
	text = text.split(" ")
	text = [str(i).lower() for i in text]
	words_to_remove = []

	for i in text:
		if i.lower() in stop_words:
			words_to_remove.append(i.lower())
	
	words_to_remove = list(set(words_to_remove))
	
	for i in words_to_remove:
		text.remove(i)
	#3del text[text.index(i)]
	
	return " ".join(text)

