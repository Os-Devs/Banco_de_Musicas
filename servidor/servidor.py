#!/usr/bin/env python3
import os
import socket
import threading

TAM_MSG = 1024   
HOST = '0.0.0.0' 
PORT = 40000     
TAM = 524288


def processa_msg_cliente(msg, con, cliente):
    msg = msg.decode()
    print('Cliente', cliente, 'enviou', msg)
    msg = msg.split()

    if msg[0].upper() == 'GET':
        nome_arq = " ".join(msg[1:])
        print('Arquivo solicitado:', nome_arq)
        try:
            status_arq = os.stat(nome_arq)
            con.send(str.encode('+OK {}\n'.format(status_arq.st_size)))
            arq = open(nome_arq, "rb")
            while True:
                dados = arq.read(TAM)
                if not dados: break
                con.send(dados)
        except Exception as e:
            con.send(str.encode('-ERR {}\n'.format(e)))

    elif msg[0].upper() == 'UP':
        nome_arq = con.recv(TAM_MSG)
        print("Recebendo", nome_arq)
        try:
            arq = open(nome_arq, "wb")
            while True:
                dado = con.recv(TAM)
                arq.write(dado)
                if not dado: break
                break
            arq.close()
        except Exception as e:
            con.send(str.encode('-ERR {}\n'.format(e)))

    elif msg[0].upper() == 'LIST':
        lista_arq = os.listdir('.')
        con.send(str.encode('+OK {}\n'.format(len(lista_arq))))
        for nome_arq in lista_arq:
            if os.path.isfile(nome_arq):
                status_arq = os.stat(nome_arq)
                con.send(str.encode('arq: {} - {:.1f}KB\n'.format(nome_arq, status_arq.st_size/1024)))
            elif os.path.isdir(nome_arq):
                con.send(str.encode('dir: {}\n'.format(nome_arq)))
            else:
                con.send(str.encode('esp: {}\n'.format(nome_arq)))

    elif msg[0].upper() == 'QUIT':
        con.send(str.encode('+OK\n'))
        return False
    else:
        con.send(str.encode('-ERR Invalid command\n'))
    return True


def processa_cliente(con, cliente):
    print('Cliente conectado', cliente)
    while True:
        msg = con.recv(TAM_MSG)
        if not msg or not processa_msg_cliente(msg, con, cliente): break
    con.close()
    print('Cliente desconectado', cliente)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv = (HOST, PORT)
sock.bind(serv)
sock.listen(50)

while True:
    try:
        con, cliente = sock.accept()
    except: break
    if os.fork() == 0:
        sock.close()
        processa_cliente(con, cliente)
        break
    else:
        con.close()
sock.close()
