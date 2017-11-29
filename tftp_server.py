#!/usr/bin/python3
# -*- coding:utf-8 -*-

import socket
import pickle
import sys,os
tftp_opcode={
	"RRQ":1,
	"WRQ":2,
	"DATA":3,
	"ACK":4,
	"ERROR":5,
}
tftp_error={
	0:"Not defined,see error message(if any).",
	1:"File not found.",
	2:"Access violation.",
	3:"Disk full or allocation exceeded.",
	4:"Illegal TFTP operation.",
	5:"Unknown transfer ID.",
	6:"File already exists.",
	7:"No Such user."
}

class tftp_server():
	def __init__(self,addr):
		self.ss=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		self.ss.bind(addr)

		self.client_addr=None

		self.file_name=None
		self.fh=None

		self.current_block_numb=0
		self.next_block_numb=1

		self.opcode=0

		self.current_data=[]
		self.data_len=512
		self.package=[]
		self.is_last=False
		self.error_numb=None


	def ntoh(self,package):
		return pickle.loads(package)
		



	def hton(self,package):
		return pickle.dumps(package)
		


	def assemble_package(self,*agrv):
		result=[]
		for n in agrv:
			result.append(n)
		return result

	def send_rrq(self,file_name):
		rrq_package=self.assemble_package(tftp_opcode['RRQ'],file_name)
		rrq_package=self.hton(rrq_package)
		self.ss.sendto(rrq_package,self.client_addr)

	def send_wrq(self):
		wrq_package=self.assemble_package(tftp_opcode['WRQ'],self.file_name)
		wrq_package=self.hton(wrq_package)
		self.ss.sendto(wrq_package,self.client_addr)

	def send_data(self):
		data_package=self.assemble_package(tftp_opcode['DATA'],self.next_block_numb,self.current_data)
		data_package=self.hton(data_package)
		print("data_package type is",type(data_package))
		self.ss.sendto(data_package,self.client_addr)
		self.next_block_numb+=1

	def send_ack(self):
		ack_package=self.assemble_package(tftp_opcode['ACK'],self.current_block_numb)
		ack_package=self.hton(ack_package)
		self.ss.sendto(ack_package,self.client_addr)

	def send_error(self,error_numb):
		erro_package=self.assemble_package(tftp_opcode['ERROR'],error_numb,tftp_error[error_numb])
		erro_package=self.ntoh(erro_package)
		self.ss.sendto(erro_package,self.client_addr)
		

	def read_file(self):
		self.current_data=self.fh.read(self.data_len)
		if len(self.current_data)<512:
			self.is_last=True


	def deal_ack(self):
		if not self.is_last:
			print("I have recv the ack block : %s"%self.current_block_numb)
			print("Now I will send the block: %d"%self.next_block_numb)
			if self.next_block_numb==self.current_block_numb+1:
				self.read_file()
				self.send_data()
			else:
				self.next_block_numb=current_block_numb+1
				self.send_data()

		else:
			print("finished")
			self.fh.close()

	def deal_data(self):
		print("Recv data block: %s"%self.next_block_numb)
		print("your last block: %s"%self.current_block_numb)
		if self.next_block_numb==self.current_block_numb+1:			
			self.fh.write(self.current_data)
			self.fh.flush()
			self.current_block_numb+=1
			self.send_ack()
		else:
			self.send_ack()


	def deal_rrq(self):
		try:
			self.fh=open(self.file_name,'rb')
			print("Openned file :  %s"%self.file_name)
			self.send_wrq()
		except IOError:
			self.fh.close()
			self.send_error(1)

	def deal_wrq(self):
		try:
			self.file_name=self.file_name[:-6]+'new.pdf'
			self.fh=open(self.file_name,'wb')
			self.send_ack()
		except IOError:
			self.fh.close()
			self.send_error(6)


	def deal_error(self):
		print(tftp_error[self.error_numb])
		

	def deal_request(self,package):
		self.package=self.ntoh(package)
		self.opcode=self.package[0]

		if self.opcode==1:
			self.file_name=self.package[1]
			self.deal_rrq()
		elif self.opcode==2:
			self.file_name=self.package[1]
			self.deal_wrq()
		elif self.opcode==3:
			self.next_block_numb=self.package[1]
			self.current_data=self.package[2]
			self.deal_data()
		elif self.opcode==4:
			self.current_block_numb=self.package[1]
			self.deal_ack()
		elif self.opcode==5:
			self.error_numb=self.package[1]
			self.deal_error()


addr=('127.0.0.1',5000)
server=tftp_server(addr)
print("Server start")
print("Waiting for...")
nb=1
while True:
	request_data,server.client_addr=server.ss.recvfrom(1024)
	server.deal_request(request_data)
	print("the %d time recv data"%nb)
	nb+=1







	


