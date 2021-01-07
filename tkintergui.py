from tkinter import *
from tkinter import ttk
import speech_recognition as sr 
import pyttsx3  
from threading import *
import sounddevice as sd
import speech_recognition as sr
import wavio
import json
from difflib import SequenceMatcher
import random
import sqlite3
import datetime
import tools
import os
import pyttsx3 
import wikipedia
import time
from selenium import webdriver
from bs4 import BeautifulSoup
import pywhatkit
from selenium.common.exceptions import NoSuchElementException
response = "Click the above button and give your voice command"
clicked = False
#intents json file
with open('intents.json') as file:
	intents = json.load(file)


#assistant Tasks
tasks = {
	
	"Youtube_search":"Youtube_search",
	"Google_search":"Google_search",
	"Info":"Info",
	"Whatsapp_msg_status":"Whatsapp_msg_status",
	"System_operation":"System_operation"
}
#pyttsx3 engine
engine = pyttsx3.init() 
engine.setProperty("rate", 178)
  
wh_questions = ["what", "when", "where"
, "who", "whom", "which", "whose", "why", "how"]

def validation(text):
	response_ratios = []
	for i in range(len(intents['intents'])):
		for j in intents['intents'][i]["patterns"]:
			ratio = SequenceMatcher(None,j.lower(),text.lower()).ratio()
			if ratio > 0.50 :
				response_ratios.append({"tag":intents['intents'][i]["tag"],"pattern":j,"ratio":ratio})
			else:
				if "play" in text.lower():
					response_obj = {
						"response":'Playing the recomended video on youtube',
						"task":'Youtube_search'
					}
					return response_obj
				if any(x in text.lower() for x in wh_questions):
					if "whatsapp" not in text:
						response_obj = {
							"response":'Opening the result on chrome tab',
							"task":'Google_search'
						}
						
					else:
						response_obj = {
							"response":'',
							"task":'Whatsapp_msg_status'
						}
					return response_obj


	max_ratios = []
	response_obj = {
		"response":'',
		"task":''
	}
	tag = ''

	if(len(response_ratios)>0):
		for j in response_ratios:
			max_ratios.append(j["ratio"])
		max_ratios_index = max_ratios.index(max(max_ratios))
		tag = response_ratios[max_ratios_index]['tag']
		
		for i in range(len(intents['intents'])):
			if intents['intents'][i]["tag"] == tag :
				if len(intents['intents'][i]["responses"])>0 :
					response_obj['response'] = random.choice(intents['intents'][i]["responses"])
					break
		for i in tasks.keys():
			
			if tasks[i] == tag:
				response_obj['task'] = i
				
		return response_obj
	else:
		return None
def listening():

	r = sr.Recognizer()
	freq = 44100
	duration = 5
	recording = sd.rec(int(duration * freq), 
	                   samplerate=freq, channels=2)

	sd.wait()
	wavio.write("recording0.wav", recording, freq, sampwidth=2)
	r = sr.Recognizer()


	text = ""
	with sr.AudioFile('recording0.wav') as source:
	    
	    audio_text = r.listen(source)
	    
	
	    try:
	        
	        # using google speech recognition
	        text = r.recognize_google(audio_text)
	        print('Converting audio transcripts into text ...')
	        print(text)
	     

	    except:
	    	engine.say("Sorry Not able to recognize your voice command try again")
	    	engine.runAndWait()

	        
	return text
def cmd(command):

	cmd = command.lower()
	processed_input = validation(cmd.lower())
	if processed_input != None :
		
		if processed_input['task'] == "Youtube_search":
			pywhatkit.playonyt(cmd.replace('play',''))
			engine.say(processed_input['response'])
			engine.runAndWait() 
		elif processed_input['task'] == "Google_search":
			
			ans = tools.clean(cmd,processed_input['task'])

			pywhatkit.search(ans)
			engine.say(processed_input['response'])
			engine.runAndWait() 
			
			
		elif processed_input['task'] == "Info":
			try:
				ans = tools.clean(cmd,processed_input['task'])
				
				data = wikipedia.summary(ans, sentences = 3) 
				
				engine.say(processed_input['response'])
				engine.runAndWait() 
				time.sleep(3)
				engine.say(data)
				engine.runAndWait() 
			except:
				engine.say("Not able to get the required informations from wikipedia")
				engine.runAndWait() 
				pass


			
		elif processed_input['task'] == "System_operation":
			if "shutdown" in cmd.lower():
				engine.say("System will shutdown in 10 seconds")
				engine.runAndWait() 
				os.system("shutdown /s /t 10")
			if "restart" in cmd.lower():
				engine.say("System will restart in 10 seconds")
				engine.runAndWait() 
				os.system("shutdown /r /t 10")
				
			if "log off" in cmd.lower():
				engine.say("System will log off in 10 seconds")
				engine.runAndWait() 
				os.system("shutdown /l /t 10")
				
			
		elif processed_input['task'] == "Whatsapp_msg_status":
			if "status" in cmd.lower():
					browser = webdriver.Chrome(executable_path=r'C:\Users\USER\Downloads\chromedriver_win32\chromedriver')
					browser.get("https://web.whatsapp.com")
					time.sleep(30)
					try:
						page_source = browser.page_source
						soup = BeautifulSoup(page_source, 'html.parser')
						div = soup.find('div',class_="_3soxC _2aY82")
						chat_list = div.find_all('div',class_="_1C6Zl")
						unread_msg=[]
						for div in chat_list:
							
							div2 = div.find('span',class_="_1hI5g _1XH7x _1VzZY").text
							
							try:
								div3 = div.find('span',class_="VOr2j").text
								unread_msg.append({"name":div2,"unread":int(div3)})
							except:
								unread_msg.append({"name":div2,"unread":0})
								pass
						unread_msg = sorted(unread_msg, key = lambda i: i['unread'],reverse=True)
						engine.say("You have not read")
						engine.runAndWait()
						for i in unread_msg:
							if i["unread"] != 0:
								 
								engine.say(str(i["unread"])+"message in"+str(i["name"]))
								engine.runAndWait()
					except Exception:
							engine.say("Not able to access your whatsapp web elements")
							engine.runAndWait() 


						
			elif "send" in cmd:
				if "whatsapp" in cmd:
					processed_msg = cmd.split(" ")
					processed_msg.pop(0)
					processed_msg.pop(len(processed_msg)-1)
					processed_msg.pop(len(processed_msg)-1)
					processed_msg.pop(len(processed_msg)-2)
					name = str(processed_msg[len(processed_msg)-1]).capitalize()
					msg = str(" ".join(processed_msg[0:len(processed_msg)-1]))
					browser = webdriver.Chrome(executable_path=r'C:\Users\USER\Downloads\chromedriver_win32\chromedriver')
					browser.get("https://web.whatsapp.com")
					time.sleep(30)
					page_source = browser.page_source
					soup = BeautifulSoup(page_source, 'html.parser')
							
					try:
						user = browser.find_element_by_xpath('//span[@title="{}"]'.format(name))
						user.click()
						msg_box = browser.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div[2]/div/div[2][@class="{}"]'.format('_1awRl copyable-text selectable-text'))
						msg_box.send_keys(msg)
						msg_button = msg_box.find_element_by_xpath('//button[@class="{}"]'.format('_2Ujuu'))
						msg_button.click()	
					except  NoSuchElementException as nse:
						search_bar =  browser.find_element_by_xpath('//*[@id="side"]/div[1]/div/label/div/div[2][@class="{}"]'.format('_1awRl copyable-text selectable-text'))
						search_bar.send_keys(name)
						time.sleep(3)
						try:
							user = browser.find_element_by_xpath('//span[@title="{}"]'.format(name))
							user.click()
							msg_box = browser.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div[2]/div/div[2][@class="{}"]'.format('_1awRl copyable-text selectable-text'))
							msg_box.send_keys(msg)
							msg_button = msg_box.find_element_by_xpath('//button[@class="{}"]'.format('_2Ujuu'))
							msg_button.click()
						except NoSuchElementException:
							engine.say("Not able to find the person in your contact list")
							engine.runAndWait()
					except Exception:
							engine.say("Not able to access your whatsapp elements")
							engine.runAndWait()



		else:
			print("None")

#Tkinter
def click_event():
	
	res["text"]="Listening ..."

	
	commands = listening()
	cmd(commands)
	res["text"]=response


window = Tk()
window.geometry("600x400") 
window.resizable(False, False)

notebook  = ttk.Notebook(window)
tab1 = Frame(notebook)
tab2 = Frame(notebook)
#tab2
commands_and_task = [{"task":"For youtube searches","command":"Play command + title of the video you want to play"},
					{"task":"For Google searches","command":"Query you want to search"},
					{"task":"For getting Information","command":"Get information about/on"},
					{"task":"For getting no of unread messages","command":"Anyone has texted  me in whatsapp/Get my whatsapp status"},
					{"task":"To send msg in whatsapp","command":"Send +message(you want to send)+ to +recipient(name)+ in whatsapp"},
					{"task":"For system operations","command":"Shutdown/restart/log off +desktop/pc/laptop/windows"}

					]
scroll_bar = Scrollbar(tab2) 
  
scroll_bar.pack( side = RIGHT, 
                fill = Y ) 
   
command_list = Listbox(tab2,  width=500,
                 yscrollcommand = scroll_bar.set ) 
command_list.insert(END, "Use the below commands for better performances") 
for line in commands_and_task: 
    command_list.insert(END, line["task"]+" - "+str(line["command"])) 
  
command_list.pack( side = LEFT, fill = BOTH ) 
  
scroll_bar.config( command = command_list.yview ) 
#tab1
tab1.configure(background='white')
photo = PhotoImage(file = "mic.png")

Button(tab1,image = photo ,command = click_event).place(relx = 0.5,  
                   rely = 0.4, 
                   anchor = 'center')
Label(tab1, text = "Voice Assistant").place(relx = 0.5,  
                   rely = 0.75, 
                   anchor = 'center')

res = Label(tab1, text = response)
res.place(relx = 0.5,  
                   rely = 0.85, 
                   anchor = 'center')
notebook.add(tab1,text="Home")
notebook.add(tab2,text="Help")

notebook.pack(expand=True,fill="both")
window.mainloop()

