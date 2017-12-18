#!/usr/bin/python

import socket

"""
*///////////////////////////////////////////////////////////////////////////////
*Relay
*Description:
*	Utility class for establishing socket communication with and send/recive
*	message to TradeGateway and StrategyCore. It establishes a client socket
*	for TradeGateway and server socket for StrategyCore.
*///////////////////////////////////////////////////////////////////////////////
"""
class Relay:
	"""
	Constructor
	Description: constructor
	"""
	def __init__(self, recv_port, trans_port):
		print('Initializing relay receiver...')
		self.receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.receiver.connect(('localhost', recv_port))		
		#print('Initializing relay transmitter...')
		#self.transmitter = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#self.transmitter.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		#self.transmitter.bind(('', trans_port))
		#print('Preprocessor waiting for connection from strategycore...')
		#self.transmitter.listen(1)
		#self.connection, client_addr = self.transmitter.accept() #Blocking till strategycore connects
	
	"""
	restart
	Description: re-establishes server socket connection with StrategyCore
	"""	
	def restart(self):
		self.connection, client_addr = self.transmitter.accept()
		
	"""
	strrev
	Description: receive string message from TradeGateway and return a tuple
	"""	
	def strrecv(self):
		message = ''
		header = self.receiver.recv(1)
		if header == '@':
			msg = self.receiver.recv(1)
			while msg != '&':
				message += msg
				msg = self.receiver.recv(1)
		return message.split('|')
	
	"""
	strsend
	Description: send message to StrategyCore through socket connection
	"""
	def strsend(self, msg):
		self.connection.send('@') #message header
		self.connection.send(msg)
		self.connection.send('&') #message footer
