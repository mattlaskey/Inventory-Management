#!/usr/bin/env python3
import sys
from flask import Flask, jsonify, abort, request, make_response, session
from flask_restful import reqparse, Resource, Api
from flask_session import Session
import json
from ldap3 import Server, Connection, ALL
from ldap3.core.exceptions import *
import pymysql
import pymysql.cursors
import ssl #include ssl libraries

import settings # Our server and db settings, stored in settings.py

application = Flask(__name__)
#CORS(app)
# Set Server-side session config: Save sessions in the local app directory.
application.config['SECRET_KEY'] = settings.SECRET_KEY
application.config['SESSION_TYPE'] = 'filesystem'
application.config['SESSION_COOKIE_NAME'] = 'peanutButter'
application.config['SESSION_COOKIE_DOMAIN'] = settings.APP_HOST

Session(application)


####################################################################################
#
# Error handlers
#
@application.errorhandler(400) # decorators to add to 400 response
def not_found(error):
	return make_response(jsonify( { 'status': 'Bad request' } ), 400)

@application.errorhandler(404) # decorators to add to 404 response
def not_found(error):
	return make_response(jsonify( { 'status': 'Resource not found' } ), 404)

@application.errorhandler(500) # decorators to add to 500 response
def not_found(error):
	return make_response(jsonify( { 'status': 'Internal server error' } ), 500)


####################################################################################
#
# Static Endpoints for humans
#
class Root(Resource):
   # get method. What might others be aptly named? (hint: post)
	def get(self):
		return application.send_static_file('index.html')


class Developer(Resource):
   # get method. What might others be aptly named? (hint: post)
	def get(self):
		return application.send_static_file('developer.html')

####################################################################################
#
# Routing: GET and POST using Flask-Session
#
class SignIn(Resource):
	#
	# Set Session and return Cookie
	#
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X POST -d '{"username": "Rick", "password": "crapcrap"}'
	#  	-c cookie-jar -k https://192.168.10.4:61340/signin
	#
	def post(self):

		if not request.json:
			abort(400) # bad request

		# Parse the json
		parser = reqparse.RequestParser()
		try:
 			# Check for required attributes in json document, create a dictionary
			parser.add_argument('username', type=str, required=True)
			parser.add_argument('password', type=str, required=True)
			request_params = parser.parse_args()
		except:
			abort(400) # bad request
		if request_params['username'] in session:
			response = {'status': 'success'}
			responseCode = 200
		else:
			try:
				ldapServer = Server(host=settings.LDAP_HOST)
				ldapConnection = Connection(ldapServer,
					raise_exceptions=True,
					user='uid='+request_params['username']+', ou=People,ou=fcs,o=unb',
					password = request_params['password'])
				ldapConnection.open()
				ldapConnection.start_tls()
				ldapConnection.bind()
				# At this point we have sucessfully authenticated.

#			if request_params['username'] == 'Rick' and request_params['password'] == 'crapcrap':
#				session['username'] = request_params['username']
#				response = {'status': 'success', 'user_id':'1'}
#				responseCode = 201
#			else:
#				response = {'status': 'Access denied'}
#				responseCode = 403
#
				session['username'] = request_params['username']
# Stuff in here to find the esiting userId or create a use and get the created userId
				try:
					dbConnection = pymysql.connect(
						settings.DB_HOST,
						settings.DB_USER,
						settings.DB_PASSWD,
						settings.DB_DATABASE,
						charset='utf8mb4',
						cursorclass= pymysql.cursors.DictCursor)
					sql = 'getUserByName'
					cursor = dbConnection.cursor()
					sqlArgs = (session['username'],)
					cursor.callproc(sql,sqlArgs) 
					user = cursor.fetchone() 
					if user is None:
						#abort(404)
						sql = 'addUser'
						admin = False;
						if session['username'] == 'rlaskey' or session['username'] == 'jpellet2':
							admin = True
						sqlArgs = (session['username'],admin)
						cursor.callproc(sql,sqlArgs)
						uid = cursor.fetchone()
					else:
						uid = user["userId"]
					dbConnection.commit()
				except:
					abort(500) 
				finally:
					cursor.close()
					dbConnection.close()
				print(uid)
				response = {'status': 'success', 'user_id': uid }
				responseCode = 201
			except LDAPException:
				response = {'status': 'Access denied'}
				print(response)
				responseCode = 403
			finally:
				ldapConnection.unbind()

		return make_response(jsonify(response), responseCode)
	# GET: Check Cookie data with Session data
	#
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X GET
	#	-b cookie-jar -k https://192.168.10.4:61340/signin
	def get(self):
		if 'username' in session:
			username = session['username']
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403

		return make_response(jsonify(response), responseCode)




	def delete(self):
		if 'username' in session:
			session['username']=None
			response= {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403
		return make_response(jsonify(response), responseCode)
####################################################################################
	
		
#
# schools routing: GET and POST, individual school access
#
class Users(Resource):
   # GET: Return all users resources. No autorizations
	# Example request: curl -i -H "Content-Type: application/json" -X GET
	# -b cookie-jar -k https://cs3103.cs.unb.ca:xxxxx/users
	def get(self):
		print("here")
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'getUsers'
			cursor = dbConnection.cursor()
			cursor.callproc(sql) # stored procedure, no arguments
			rows = cursor.fetchall() # get all the results
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify({'users': rows}), 200) # turn set into json and return it

	def post(self):
		"""
		if 'username' in session:
			username = session['username']
			print("current: " + username)
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail', 'message': 'Access Denied'}
			responseCode = 403
			return make_response(jsonify(response), responseCode)
		if not request.json or not 'Name' in request.json:
			response = {'status': 'fail', 'message': 'Bad Request'}
			responseCode = 400
			return make_response(jsonify(response), responseCode)
		"""
		response = {'status': 'success'}
		responseCode = 200
		name = request.json['Name']
		admin = False

		try:
			dbConnection = pymysql.connect(settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'addUser'
			cursor = dbConnection.cursor()
			sqlArgs = (name, admin)
			cursor.callproc(sql,sqlArgs)
			row = cursor.fetchone()
			dbConnection.commit()
		except:
			abort(500)
		finally:
			cursor.close()
			dbConnection.close()
		# Return user ID
		ID = row['LAST_INSERT_ID()']
		

class UserId(Resource):
    # GET: Return identified user resource
	#
	# Example request: curl -i -H "Content-Type: application/json" -X GET
	# -b cookie-jar -k https://cs3103.cs.unb.ca:xxxxx/users/1
	#
	def get(self, userId):
		print("here2")
		if 'username' in session:
			username = session['username']
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'getUserById'
			cursor = dbConnection.cursor()
			sqlArgs = (userId,)
			cursor.callproc(sql,sqlArgs) # stored procedure, no arguments
			row = cursor.fetchall() # get the single result
			if row is None:
				abort(404)
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify({"user": row}), 200) # successful
		
	def delete(self, userId):
		if 'username' in session:
			username = session['username']
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403

		# Get executing user
		try:
			dbConnection = pymysql.connect(settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'getUserByName'
			cursor = dbConnection.cursor()
			sqlArgs = (username,)
			cursor.callproc(sql,sqlArgs)
			user = cursor.fetchone()
			if user is None:
				abort(404)
			else:
				uid = user["userId"]
		except:
			abort(500)
		finally:
			cursor.close()
			dbConnection.close()
		
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			cursor = dbConnection.cursor()
			#first remove all of that users presents because userId is foreign key
			sql = 'getPresentsByUser'
			cursor = dbConnection.cursor()
			sqlArgs = (userId,)
			cursor.callproc(sql,sqlArgs) 
			rows = cursor.fetchall() 
			sql = 'removePresent'
			#for each pid in row, remove the present
			for row in rows:
				sqlArgs = (row['presentId'], userId,)
				cursor.callproc(sql,sqlArgs)
				dbConnection.commit()
			#
			sql = 'removeUser'
			sqlArgs = (userId, uid,)
			cursor.callproc(sql,sqlArgs)
			dbConnection.commit()
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify({"status": "success"}), 200) # successful

class UserName(Resource):
    # GET: Return identified user resource
	#
	# Example request: curl -i -H "Content-Type: application/json" -X GET
	# -b cookie-jar -k https://cs3103.cs.unb.ca:xxxxx/users/testing
	#
	def get(self, userName):
		if 'username' in session:
			username = session['username']
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'getUserByName'
			cursor = dbConnection.cursor()
			sqlArgs = (userName,)
			cursor.callproc(sql,sqlArgs) # stored procedure, no arguments
			row = cursor.fetchall() # get the single result
			if row is None:
				abort(404)
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify({"user": row}), 200) # successful


class Presents(Resource):
	# GET: Return identified present resource
	# Example request: curl -i -H "Content-Type: application/json" -X GET
	# -b cookie-jar -k https://cs3103.cs.unb.ca:xxxxx/presents
	def get(self):
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'getAllPresents'
			cursor = dbConnection.cursor()
			cursor.callproc(sql) # stored procedure, no arguments
			rows = cursor.fetchall() # get all the results
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
#			print("testing")
			#if(rows is not None):
			#rows = str(rows)   
#			for i in rows:
				#if rows[i][4] != None:
				#	rows[i][4]=""+rows[i][4]
			dbConnection.close()
		return make_response(jsonify({'presents': rows}), 200) # turn set into json and return it
		
class PresentUser(Resource):
    # GET: Return identified user resource
	#
	# Example request: curl -i -H "Content-Type: application/json" -X GET
	# -b cookie-jar -k https://cs3103.cs.unb.ca:xxxxx/present/2
#
	def get(self, userId):
		if 'username' in session:
			username = session['username']
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'getPresentsByUser'
			cursor = dbConnection.cursor()
			sqlArgs = (userId,)
			cursor.callproc(sql,sqlArgs) # stored procedure, no arguments
			row = cursor.fetchall() # get the single result
			if row is None:
				abort(404)


		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify({"presents": row}), 200) # successful

	def post(self, userId):
		if 'username' in session:
			username = session['username']
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail', 'message': 'Access Denied'}
			responseCode = 403
			return make_response(jsonify(response), responseCode)
		if not request.json or not 'presentName' in request.json or not 'presentPrice' in request.json:
			response = {'status': 'fail', 'message': 'Bad Request'}
			responseCode = 400
			return make_response(jsonify(response), responseCode)

		presentName = request.json["presentName"]
		presentPrice = request.json["presentPrice"]

		if 'presentDesc' in request.json:
			presentDesc = request.json["presentDesc"]
		else:
			presentDesc = ''
		
		# Check user credentials
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'getUserByName'
			cursor = dbConnection.cursor()
			sqlArgs = (username,)
			cursor.callproc(sql,sqlArgs) 
			user = cursor.fetchone() 
			if user is None:
				abort(404)
			dbConnection.commit()
		except:
			abort(500) 
		finally:
			cursor.close()
			dbConnection.close()

		if user["userId"] != userId and not user["admin"]:
			response = {'status': 'fail', 'message': 'Access Denied'}
			responseCode = 403
			return make_response(jsonify(response), responseCode)

		# add Present
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'addPresent'
			cursor = dbConnection.cursor()
			sqlArgs = (userId, presentName, presentDesc, presentPrice,)
			cursor.callproc(sql,sqlArgs) 
			row = cursor.fetchone() 
			if row is None:
				abort(404)
			dbConnection.commit()
		except:
			abort(500) 
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify({"status": "success", "present": row}), 200) # successful

class PresentName(Resource):
    # GET: Return identified user resource
	#
	# Example request: curl -i -H "Content-Type: application/json" -X GET
	# -b cookie-jar -k https://cs3103.cs.unb.ca:xxxxx/presents/testing
	#
	def get(self, presentName):
		if 'username' in session:
			username = session['username']
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'getPresentByName'
			cursor = dbConnection.cursor()
			sqlArgs = (presentName,)
			cursor.callproc(sql,sqlArgs) # stored procedure, no arguments
			row = cursor.fetchall() # get the single result
			if row is None:
				abort(404)


		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify({"presents": row}), 200) # successful

class PresentId(Resource):
    # GET: Return identified user resource
	#
	# Example request: curl -i -H "Content-Type: application/json" -X GET
	# -b cookie-jar -k https://cs3103.cs.unb.ca:xxxxx/presents/1
	#
	def get(self, presentId):
		if 'username' in session:
			username = session['username']
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'getPresentById'
			cursor = dbConnection.cursor()
			sqlArgs = (presentId,)
			cursor.callproc(sql,sqlArgs) # stored procedure, no arguments
			row = cursor.fetchall() # get the single result
			if row is None:
				abort(404)


		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify({"presents": row}), 200) # successful

	def post(self, presentId):
		if 'username' in session:
			username = session['username']
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403
		if not request.json:
			abort(400)

		# Get executing user
		try:
			dbConnection = pymysql.connect(settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'getUserByName'
			cursor = dbConnection.cursor()
			sqlArgs = (username,)
			cursor.callproc(sql,sqlArgs)
			user = cursor.fetchone()
			if user is None:
				abort(404)
		except:
			abort(500)
		finally:
			cursor.close()
			dbConnection.close()

		userId = user["userId"]
		presentName = request.json["presentName"]
		presentDesc = request.json["presentDesc"]
		presentPrice = request.json["presentPrice"]
		
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'updatePresent'
			cursor = dbConnection.cursor()
			sqlArgs = (presentId, presentName, presentDesc, presentPrice, userId)
			cursor.callproc(sql,sqlArgs) # stored procedure, no arguments
			dbConnection.commit()
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify({"status": "success"}), 200) # successful

	def delete(self, presentId):
		if 'username' in session:
			username = session['username']
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403

		# Get executing user
		try:
			dbConnection = pymysql.connect(settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'getUserByName'
			cursor = dbConnection.cursor()
			sqlArgs = (username,)
			cursor.callproc(sql,sqlArgs)
			user = cursor.fetchone()
			if user is None:
				abort(404)
			else:
				uid = user["userId"]
		except:
			abort(500)
		finally:
			cursor.close()
			dbConnection.close()
		
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'removePresent'
			cursor = dbConnection.cursor()
			sqlArgs = (presentId, uid)
			cursor.callproc(sql,sqlArgs) # stored procedure, no arguments
			dbConnection.commit()
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify({"status": "success"}), 200) # successful
			
class PresentPrice(Resource):
    # GET: Return identified user resource
	#
	# Example request: curl -i -H "Content-Type: application/json" -X GET
	# -b cookie-jar -k https://cs3103.cs.unb.ca:xxxxx/present/2.60
	#
	def get(self, presentPrice):
		if 'username' in session:
			username = session['username']
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			presentPrice=float(presentPrice)
			sql = 'getPresentByPrice'
			cursor = dbConnection.cursor()
			sqlArgs = (presentPrice,)
			cursor.callproc(sql,sqlArgs) # stored procedure, no arguments
			row = cursor.fetchall() # get the single result
			if row is None:
				abort(404)


		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify({"presents": row}), 200) # successful




####################################################################################
#
# Identify/create endpoints and endpoint objects
#
api = Api(application)
api.add_resource(Root,'/')
api.add_resource(Developer,'/dev')
api.add_resource(SignIn, '/signin')
api.add_resource(Users, '/users')
api.add_resource(UserId, '/users/<int:userId>')
api.add_resource(UserName, '/users/<string:userName>')
api.add_resource(Presents, '/presents')
api.add_resource(PresentUser, '/present/<int:userId>')
api.add_resource(PresentName, '/presents/<string:presentName>')
api.add_resource(PresentId, '/presents/<int:presentId>')
api.add_resource(PresentPrice, '/present/<string:presentPrice>')


#############################################################################
# xxxxx= last 5 digits of your studentid. If xxxxx > 65535, subtract 30000
if __name__ == "__main__":
	#
	# You need to generate your own certificates. To do this:
	#	1. cd to the directory of this app
	#	2. run the makeCert.sh script and answer the questions.
	#	   It will by default generate the files with the same names specified below.
	#
	context = ('cert.pem', 'key.pem') # Identify the certificates you've generated.
	application.run(
		host=settings.APP_HOST,
		port=settings.APP_PORT,
		ssl_context=context,
		debug=settings.APP_DEBUG)

