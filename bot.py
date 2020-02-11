from flask import Flask
from flask import request, render_template, jsonify
from configparser import ConfigParser
from pyparsing import Word, alphas, nums
from pymongo import MongoClient
import requests
import json
import os

app = Flask(__name__)

class CountAdminsMustBeNotNull(Exception):
	def __init__(self):
		print('Admins_count cannot be 0')
		exit()

global token
global URL
global mongo_user
global mongo_pass
global mongo_url
global permission

permission = False

config = ConfigParser()
# "config.ini" it's yours config file
config.read(os.getcwd() + "/config.ini")
# here we're geting token from config.ini
token = config.get("default", "token")
# our url	
URL = "https://api.telegram.org/bot{}/".format(token)
# count of users from config.ini
users_count = config["allowed-users"]["users_count"]
# geting admins
admins_count = config["admins"]["admins_count"]

# making admins
if admins_count == '0':
	raise CountAdminsMustBeNotNull()
else:
	# make a list for admins
	admins = [i for i in range(0,int(admins_count))]
	# add to list admins
	for a in range(0,int(admins_count)):
		admins[a] = config["admins"]["admin" + str(a)]

# checking if allowed access to all users
if users_count == '*':
	permission = True
else:
	# make a list for users
	users = [i for i in range(0,int(users_count))]
	# add to list users
	for user in range(0,int(users_count)):
		users[user] = config["allowed-users"]["user" + str(user)]

# geting mongo_user, mongo_pass and mongo_url from config.ini
mongo_user = config.get("mongodb", "user")
mongo_pass = config.get("mongodb", "password")
mongo_url = config.get("mongodb", "mongo_url").format(mongo_user, mongo_pass)

# connecting to db
try:
	client = MongoClient(mongo_url)
except:
	print('Cannot connect to db')

# connect to collection money
db = client.money
mongo_money = db.money

# get 
def get_from_mongodb_all_money(user_id, chat_id, mongo_money):
	f = mongo_money.find_one({"user_id": user_id})
	if not f == None:
		all_money = {'have': 0, 'debt': 0, 'loan': 0, 'spent': 0}
		all_money['have'] = f['have']
		all_money['debt'] = f['debt']
		all_money['loan'] = f['loan']
		all_money['spent'] = f['spent']
		m = all_money['have'] - all_money['debt']
		m -=  all_money['loan']
		m -= all_money['spent']
		text = 'U\'ve ' + str(m) + ' uan'
		have_permission(user_id)(chat_id, text)
	else:
		have_permission(user_id)(chat_id, 'We haven\'t any data about you')
		have_permission(user_id)(chat_id, 'If you recently delete your data \nsend /start to make data')

# add to mongodb our data
def add_to_mongodb(user_id, chat_id, m, h):
	f = mongo_money.find_one({"user_id": user_id})
	if not f == None:
		result = mongo_money.update_many({"user_id": user_id}, {'$inc':{m: h}})
		text = "Add to {0} {1} uan".format(m, h)
		have_permission(user_id)(chat_id, text)
	else:
		have_permission(user_id)(chat_id, 'We haven\'t any data about you')
		have_permission(user_id)(chat_id, 'If you recently delete your data \nsend /start to make data')

# main logic
@app.route('/', methods=['POST', 'GET'])
def index():
	if request.method == 'POST':
		r = request.get_json()
		chat_id = r['message']['chat']['id']
		message = r['message']['text']
		try:
			user_name = r['message']['from']['username']
		except KeyError:
			user_name = r['message']['from']['first_name']
		user_id = chat_id
		if message == '/start':
			f = mongo_money.find_one({"user_id": user_id})
			if not f == None:
				have_permission(user_id)(chat_id, 'Why u send it?')
			else:
				have_permission(user_id)(chat_id, 'hi')
				new_money = [{"user_id": user_id,
				'username': user_name,
				'have': 0,
				'debt': 0,
				'loan': 0,
				'spent': 0
				}]

				result = mongo_money.insert_many(new_money)

		elif message == '/null':

			try:
				result = mongo_money.delete_many({"user_id": user_id})
				have_permission(user_id)(chat_id, 'Successfuly deleted all data')
				have_permission(user_id)(chat_id, 'Send /start to make data')
			except:
				have_permission(user_id)(chat_id, 'Cannot delete your data')

		elif message == '/statistics':

			permission = False
			for a in range(0,int(admins_count)):
				if int(user_id) == int(admins[int(a)]):
					permission = True 
					cursor = mongo_money.find({})
					for document in cursor:
						send_message(chat_id, 'Username: ' + document['username'])
					break
			else:
				if not permission:
					send_message(chat_id, text='403 forbidden')

		elif message == '/help':
			have_permission(user_id)(chat_id, 'Usage:\n /h 54 - u have 54 uan,\n /s 24 - u spent 24 uan,\n /d 67 - u have debt 67 uan,\n /l 76 - u give a loan 76 uan,\n /m - all money u have now,\n /null delete all data about you ')
		else:
			answer = parse(message)

			if answer[1] == 'h':
				check_argument(user_id, chat_id, 'have', answer)
			elif answer[1] == 'd':
				check_argument(user_id, chat_id, 'debt', answer)
			elif answer[1] == 'l':
				check_argument(user_id, chat_id, 'loan', answer)
			elif answer[1] == 's':
				check_argument(user_id, chat_id, 'spent', answer)
			elif answer[1] == 'm':
				get_from_mongodb_all_money(user_id, chat_id, mongo_money)
			else:
				text = ' I can\'t understand this command'
				have_permission(user_id)(chat_id, text)

		return jsonify(r)
	return "<h1>Hi</h1>"

# error 404
@app.errorhandler(404)
def not_found(error):
	return render_template('error.html')

# checking permission for user
def have_permission(user_id):
	def inner(chat_id, text):
		if not users_count == '*':
			permission = False
			for u in range(0,int(users_count)):
				if int(user_id) == int(users[int(u)]):
					permission = True 
					send_message(chat_id, text)
					break
			else:
				if not permission:
					send_message(chat_id, text='403 forbidden')
		else:
			send_message(chat_id, text)
	return inner

# send message 
def send_message(chat_id, text='hi, I\'ve just start working'):
	answer = {'chat_id': chat_id, 'text': text}
	r = requests.post(URL + "sendmessage", json=answer)

# parsing text, here I find command
def parse(text):
	try:
		greet = '/' + Word(alphas) + Word(nums)
		greeting = greet.parseString(text)
		return greeting
	except:
		try:
			greet = '/' + Word(alphas)
			greeting = greet.parseString(text)
			return greeting
		except:
			error = 'error'
			return error

# here we're checking if command is /h 54 or something like this
def check_argument(user_id, chat_id, h, answer):
	try:
		add_to_mongodb(user_id, chat_id, h, int(answer[2]))
	except:
		text = 'I need a number as argument'
		have_permission(user_id)(chat_id, text)

if __name__ == '__main__':
	app.run()