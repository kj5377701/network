import socket
import threading
import sys
from ffff import hexdump, request_handler, receive_from, response_handler


def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)
        remote_buffer = response_handler(remote_buffer)
        if len(remote_buffer):
            print('sending %d bytes to localhost.' % len(remote_buffer))
            client_socket.send(remote_buffer)

    while 1:
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            print('receive %d bytes from localhost.' % len(local_buffer))
            hexdump(local_buffer)

            local_buffer = request_handler(local_buffer)

            remote_socket.send(local_buffer)
            print('send to remote.')
        remote_buffer = receive_from(remote_socket)

        if len(remote_buffer):
            print('receive %d bytes from remote.' % len(remote_buffer))
            hexdump(remote_buffer)

            remote_buffer = response_handler(remote_buffer)

            client_socket.send(remote_buffer)

            print('send to localhost.')

            if not len(local_buffer) or not len(remote_buffer):
                client_socket.close()
                remote_socket.close()
                print('no more data.coseing connection.')
                break


def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((local_host, local_port))

    except:
        print('fail to listen on: ', local_host)
        sys.exit(0)
    print('listening on: ', local_host)

    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        print('receive from: ', addr[0])

        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()


def main():
    if len(sys.argv[1:]) != 5:
        print('use right argv.(need 5)')
        sys.exit(0)

    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    receive_first = sys.argv[5]
    if 'True' in receive_first:
        receive_first = True
    else:
        receive_first = False
    server_loop(local_host, local_port, remote_host, remote_port, receive_first)
