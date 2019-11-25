from flask import Flask
from flask import request
import time
import json
import hashlib
import pymysql
from pymysql.cursors import DictCursor
app = Flask(__name__)

connection = pymysql.connect(
	host='185.148.82.46',
	user='admin_blockchain',
	password='blockchain',
	db='admin_blockchain',
	charset='utf8mb4',
	cursorclass=DictCursor
)

def check_balance_fun(str):
	with connection.cursor() as cursor:
		query1 = 'SELECT * FROM transaction WHERE public_key = %s'
		cursor.execute(query1, (str))
		t1 = cursor.fetchall()
		sum = 0
		for row in t1:
			sum += row['amount']
		query2 = 'SELECT * FROM transaction WHERE to_whom_public = %s'
		cursor.execute(query2, (str))
		t2 = cursor.fetchall()
		sum1 = 0
		for row in t2:
			sum1 += row['to_whom_amount']
		return (sum1 - sum)

def the_wholeness_of_the_chain():
	connection.ping(reconnect=True)
	with connection.cursor() as cursor:
		query = 'SELECT * FROM `transaction`'
		cursor.execute(query)
		t = cursor.fetchall()
		c = t[0]['hash']
		for row1 in t:
			tmp = row1['prev_hash']
			if c == tmp or c == "NULL":
				return 0
	return 1

def checking_haching_info():
	connection.ping(reconnect=True)
	with connection.cursor() as cursor:
		query = 'SELECT * FROM `transaction`'
		cursor.execute(query)
		t = cursor.fetchall()
		for row in t:
			t = generate_hash(row['prev_hash'], row['public_key'], str(float(row['amount'])),row['to_whom_public'], str(row['time_stmp']))
			c = row['hash']
			print(t, '\t', c)
			if t != c:
				print ("error")
				return 1
	print("All ok 2")
	return 0

@app.route('/check_balance', methods=['POST'])
def check_balance():
	connection.ping(reconnect=True)
	the_address = request.form.get('public_key')
	print (the_address)
	print(len(the_address))
	if (len(the_address) == 64):
		res = str(check_balance_fun(the_address))
	else:
		res = "Incorrect input of address"
	return res

@app.route('/block_info', methods=['POST'])
def block_info():
	connection.ping(reconnect=True)
	with connection.cursor() as cursor:
		cursor.execute('SELECT * FROM `transaction` WHERE `hash` = %s', request.form.get('hash'))
	return json.dumps(cursor.fetchone())

@app.route('/all_tranaction', methods=['POST'])
def all_tranactiocn():
	print('1123123123')
	connection.ping(reconnect=True)
	str = request.form.get('public_key')
	with connection.cursor() as cursor:
		query1 = 'SELECT * FROM transaction WHERE public_key = %s'
		cursor.execute(query1, (str))
		t1 = cursor.fetchall()
		query2 = 'SELECT * FROM transaction WHERE to_whom_public = %s'
		cursor.execute(query2, (str))
		t2 = cursor.fetchall()
	if not t1 and not t2:
		return json.dumps(0)
	elif not t1:
		return json.dumps(t2)
	elif not t2:
		return json.dumps(t1)
	return json.dumps(t1 + t2)

@app.route('/last_hash', methods=['POST'])
def last_hash():
	connection.ping(reconnect=True)
	with connection.cursor() as cursor:
		cursor.execute('SELECT `hash` FROM `transaction` ORDER BY id DESC LIMIT 1')
	return json.dumps(cursor.fetchone())

def generate_hash(prev_hash, public_key, amount, to_whom_public, time):
	hash = hashlib.sha256()
	hash.update(prev_hash.encode('utf-8'))
	hash.update(public_key.encode('utf-8'))
	hash.update(amount.encode('utf-8'))
	hash.update(to_whom_public.encode('utf-8'))
	hash.update(time.encode('utf-8'))
	return hash.hexdigest()

@app.route('/make_transaction', methods=['POST'])
def make_tranaction():
	mas_trans = request.form.get('mas_trans')
	mas_trans = json.loads(mas_trans)
	timestamp = str(int(time.time()))
	# print(mas_trans)
	# print(timestamp)
	if (checking_haching_info() == 0) and (the_wholeness_of_the_chain() == 0):
		with connection.cursor() as cursor:
			last_block = generate_hash(json.loads(last_hash())['hash'], mas_trans['publ_key'], str(float(mas_trans['the_summ'])), mas_trans['to_whom_publ_key'], timestamp);
			cursor.execute('INSERT INTO transaction (`prev_hash`, `public_key`, `amount`, `to_whom_public`, `to_whom_amount`, `time_stmp`, `hash`) VALUES (%s, %s, %s, %s, %s, %s, %s)', (json.loads(last_hash())['hash'], mas_trans['publ_key'], str(float(mas_trans['the_summ'])), mas_trans['to_whom_publ_key'], str(float(mas_trans['the_summ'])), timestamp, last_block))
			connection.commit()
		return "the transaction is SUCCESS"
	else:
		return "the chain was broken"

if __name__ == '__main__':
	app.run(debug = True)