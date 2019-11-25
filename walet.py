import hashlib
from struct import Struct
from random import SystemRandom
from binascii import hexlify
import requests
import json
import base58
import pymysql
from pymysql.cursors import DictCursor

class color:

	Red = '\033[91m'
	Green = '\033[92m'
	Yellow = '\033[93m'
	Blue = '\033[94m'
	Magenta = '\033[95m'
	Cyan = '\033[96m'
	END = '\033[0m'

connection = pymysql.connect(
	host='185.148.82.46',
	user='admin_blockchain',
	password='blockchain',
	db='admin_blockchain',
	charset='utf8mb4',
	cursorclass=DictCursor
)

SYS_RAN = SystemRandom()
PACKER = Struct('>QQQQ')
MIN_VAL = 0x1
MAX_VAL = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141

def make_privat_key():
	key = SYS_RAN.randint(MIN_VAL, MAX_VAL)
	key0 = key >> 192
	key1 = (key >> 128) & 0xffffffffffffffff
	key2 = (key >> 64) & 0xffffffffffffffff
	key3 = key & 0xffffffffffffffff
	return hexlify(PACKER.pack(key0, key1, key2, key3))

def make_public_key(my_privat_key):
	sha_pub = hashlib.sha256()
	sha_pub.update(my_privat_key.encode('utf-8'))
	return sha_pub.hexdigest()

def check_balance(my_publ_key):
	print(color.Blue + "\n It is BALANCE MENU\n"+ color.END)
	print("Press '1' to Check your balance")
	print("Press '2' to Check balance, using address")
	print("Press '9' to come back to MAIN MENU")
	print("Press '0' to quit")
	a = input(color.Yellow +"What is your choice?\n"+ color.END)
	if a == '1':
		data = requests.post("http://localhost:5000/check_balance", data={'public_key': my_publ_key})
		print(color.Green +"The balance is:"+ color.END, data.text)
		check_balance(my_publ_key)
		return data.text
	if a == '2':
		the_address = input(color.Yellow +"Input the address(publick key), you want to check:\n"+ color.END)
		data = requests.post("http://localhost:5000/check_balance", data={'public_key': the_address})
		print(color.Green +"The balance is:"+ color.END, data.text)
		check_balance(my_publ_key)
		return data.text
	elif a == '9':
		wallet(my_publ_key)
	elif a == '0':
		quit()

def block_info(my_publ_key):
	hash_get = input(color.Yellow +"What is the hash, you want to know about?\n"+ color.END)
	r = requests.post("http://localhost:5000/block_info", data={'hash': hash_get})
	print(r.text[:200000])
	wallet(my_publ_key)

def all_tranaction(my_publ_key):
	print(color.Blue + "\n It is transaction MENU\n" + color.END)
	print("Press '1' to Check your transactions")
	print("Press '2' to Check transactions, using address")
	print("Press '9' to come back to MAIN MENU")
	print("Press '0' to quit")
	a = input(color.Yellow + "What is your choice?\n"+ color.END)
	if a == '1':
		res = requests.post("http://localhost:5000/all_tranaction", data={'public_key': my_publ_key})
		print(res.text)
		all_tranaction(my_publ_key)
	if a == '2':
		other_publick_key = input(color.Yellow + "to watch all your transaction input Publickey:\n" + color.END)
		res = requests.post("http://localhost:5000/all_tranaction", data={'public_key': other_publick_key})
		print(res.text)
		all_tranaction(my_publ_key)
	elif a == '9':
		wallet(my_publ_key)
	elif a == '0':
		quit()

def make_transaction(my_publ_key):
	mas_trans = {}
	mas_trans["priv_key"] = input("Input your Private Key\n")
	mas_trans["publ_key"] = input("Input your Public Key\n")
	mas_trans["the_summ"] = input("How much do you want to send\n")
	mas_trans["to_whom_publ_key"] = input("To whom do you want to send your OK_Coin?\n")
	r = requests.post("http://localhost:5000/make_transaction", data={'mas_trans': json.dumps(mas_trans)})
	if (r.text != "the transaction is SUCCESS"):
		print(color.Red +"the chain was broken"+ color.END)
	if (r.text == "the transaction is SUCCESS"):
		print(color.Green +"The transaction is SUCCESS"+ color.END)
		last_hash = requests.post("http://localhost:5000/last_hash")
		print(last_hash.text)
	wallet(my_publ_key)

def wallet(my_publ_key):
	print(color.Blue +"\n It is MAIN MENU of MASTER EXPRESSION WALLET\n"+ color.END)
	print("Press '1' to Check your balance, using address")
	print("Press '2' to get info of some block")
	print("Press '3' to watch all your transaction")
	print("Press '4' to make a new transaction")
	print("Press '9' to come back to Authorization Form")
	print("Press '0' to quit")
	a = input(color.Yellow +"What is your choice?\n"+ color.END)
	if a == '1':
		check_balance(my_publ_key)
	elif a == '2':
		block_info(my_publ_key)
	elif a == '3':
		all_tranaction(my_publ_key)
	elif a == '4':
		make_transaction(my_publ_key)
	elif a == '9':
		main()
	elif a == '0':
		quit()
	else:
		print("YOU choose non-existent variant... Try again.")
		wallet(my_publ_key)

def main():
	print (color.Blue +"\n	It is SUPPER_MEGA_Coin of blockchain_genesis\n"+ color.END)
	print ("Chose one of the next operations:")
	print ("Press '1' to Signin")
	print ("Press '2' to Register")
	print ("Press '0' to Quit")
	a = input(color.Yellow +"What is your choice?\n"+ color.END)
	if a == '1':
		Login = input(color.Yellow +"To Signin - write your Login:"+ color.END)
		Password = input(color.Yellow +"Now - write your Password:"+ color.END)
		with connection.cursor() as cursor:
			connection.ping(reconnect=True)
			query = 'SELECT * FROM users WHERE login = %s AND password = %s'
			t = cursor.execute(query,(Login, Password))
			if t == 1:
				query = 'SELECT * FROM users WHERE login = %s'
				cursor.execute(query, (Login))
				t = cursor.fetchone()
				wallet(t['public_key'])
			if t == 0:
				print(color.Red +"\nThe Login or Password is wrong. You are sent to the Authorization Form."+ color.END)
				main()
	elif a == '2':
		Login = input(color.Yellow +"Write your Login (it must contains only digit's and letter's):"+ color.END)
		while Login.isalnum() != 1:
			Login = input(color.Yellow +"Login:"+ color.END)
		Password = input(color.Yellow +"Write your Password (It must contains only digit's and letter's and Length must be more then 8 symbols):"+ color.END)
		while (len(Password) < 8) or (not Password.isalnum() == 1):
			Password = input(color.Yellow +"Password:"+ color.END)
		with connection.cursor() as cursor:
			connection.ping(reconnect=True)
			query = 'SELECT * FROM users WHERE login = %s'
			t = cursor.execute(query, (Login))
			if t == 1:
				print(color.Red +"SORRY, this login is occupied. Try to choose another one"+ color.END)
				main()
			if t == 0:
				my_privat_key = make_privat_key().decode('utf-8')
				my_pubick_key = make_public_key(my_privat_key)
				query = 'INSERT INTO `users` (`login`, `password`, `privat_key`, `public_key`) VALUES (%s, %s, %s, %s)'
				cursor.execute(query,(Login, Password, my_pubick_key, my_privat_key))
				connection.commit()
				print(color.Cyan +"\n	There are your PrivatKey and PublicKey.\nThey are used to sign and verify any transactions that you make.\nAnd you share just the public key, you NEVER share your private key,\nbecause if you do so everyone can access and use your money. \nSAVE IT IN THE SAFE PLACE.\n"+ color.END)
				print(color.Green +"PrivatKey:"+ color.END, my_pubick_key)
				print(color.Green +"PublicKey:"+ color.END, my_privat_key)
				main()
	elif a == '0':
		quit()
	else:
		print(color.Blue +"YOU DOESN'T WANT TO DO WHAT YOU SHOULD TO DO... Try again.")
		main()

main()