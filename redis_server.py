import socket
import threading

from resp_encoder import RESPEncoder
from resp_parser import RESPParser

class RedisServer:
    def __init__(self, host='localhost', port=6379):
        self.host = host
        self.port = port
        self.storage = {}  # Our in-memory key-value store
        self.commands = {
            'PING': self.handle_ping,
            'SET': self.handle_set,
            'GET': self.handle_get,
            'DEL': self.handle_del,
            'EXISTS': self.handle_exists,
            'INCR': self.handle_incr,
            'DECR': self.handle_decr,
            'LPUSH': self.handle_lpush,
            'RPUSH': self.handle_rpush,
            'LPOP': self.handle_lpop,
            'RPOP': self.handle_rpop,
            'LLEN': self.handle_llen,
            'LRANGE': self.handle_lrange,
        }
    
    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        
        print(f"Redis server listening on {self.host}:{self.port}")
        
        while True:
            client_socket, address = server_socket.accept()
            print(f"Client connected from {address}")
            
            client_thread = threading.Thread(
                target=self.handle_client,
                args=(client_socket,)
            )
            client_thread.start()
    
    def handle_client(self, client_socket):
        parser = RESPParser()
        
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                parser.feed(data)
                
                # Parse and process commands
                while True:
                    try:
                        command = parser.parse_message()
                        if command is None:
                            break
                        
                        print(f"Received command: {command}")  # Debug print
                        
                        response = self.process_command(command)
                        encoded_response = RESPEncoder.encode(response)
                        
                        print(f"Sending response: {encoded_response}")  # Debug print
                        client_socket.send(encoded_response)
                        
                    except Exception as e:
                        print(f"Error processing command: {e}")  # Debug print
                        error_response = RESPEncoder.encode(Exception(str(e)))
                        client_socket.send(error_response)
                        break
                        
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()
    
    def process_command(self, command):
        if not isinstance(command, list) or len(command) == 0:
            return Exception("Invalid command format")
        
        cmd_name = command[0].upper()
        cmd_args = command[1:]
        
        if cmd_name in self.commands:
            return self.commands[cmd_name](cmd_args)
        else:
            return Exception(f"Unknown command: {cmd_name}")
    
    # Command handlers
    def handle_ping(self, args):
        if args:
            return args[0]
        return "PONG"
    
    def handle_set(self, args):
        if len(args) < 2:
            return Exception("Wrong number of arguments for SET")
        
        key, value = args[0], args[1]
        self.storage[key] = value
        return "OK"
    
    def handle_get(self, args):
        if len(args) != 1:
            return Exception("Wrong number of arguments for GET")
        
        key = args[0]
        return self.storage.get(key)
    
    def handle_del(self, args):
        if len(args) == 0:
            return Exception("Wrong number of arguments for DEL")
        
        deleted_count = 0
        for key in args:
            if key in self.storage:
                del self.storage[key]
                deleted_count += 1
        
        return deleted_count
    
    def handle_exists(self, args):
        if len(args) == 0:
            return Exception("Wrong number of arguments for EXISTS")
        
        exists_count = 0
        for key in args:
            if key in self.storage:
                exists_count += 1
        
        return exists_count
    
    def handle_incr(self, args):
        if len(args) != 1:
            return Exception("Wrong number of arguments for INCR")
        
        key = args[0]
        if key not in self.storage:
            self.storage[key] = "0"
        
        try:
            current_value = int(self.storage[key])
            new_value = current_value + 1
            self.storage[key] = str(new_value)
            return new_value
        except ValueError:
            return Exception("Value is not an integer")
    
    def handle_decr(self, args):
        if len(args) != 1:
            return Exception("Wrong number of arguments for DECR")
        
        key = args[0]
        if key not in self.storage:
            self.storage[key] = "0"
        
        try:
            current_value = int(self.storage[key])
            new_value = current_value - 1
            self.storage[key] = str(new_value)
            return new_value
        except ValueError:
            return Exception("Value is not an integer")
    
    # List operations
    def handle_lpush(self, args):
        if len(args) < 2:
            return Exception("Wrong number of arguments for LPUSH")
        
        key = args[0]
        values = args[1:]
        
        if key not in self.storage:
            self.storage[key] = []
        
        if not isinstance(self.storage[key], list):
            return Exception("Operation against a key holding the wrong kind of value")
        
        for value in reversed(values):
            self.storage[key].insert(0, value)
        
        return len(self.storage[key])
    
    def handle_rpush(self, args):
        if len(args) < 2:
            return Exception("Wrong number of arguments for RPUSH")
        
        key = args[0]
        values = args[1:]
        
        if key not in self.storage:
            self.storage[key] = []
        
        if not isinstance(self.storage[key], list):
            return Exception("Operation against a key holding the wrong kind of value")
        
        self.storage[key].extend(values)
        return len(self.storage[key])
    
    def handle_lpop(self, args):
        if len(args) != 1:
            return Exception("Wrong number of arguments for LPOP")
        
        key = args[0]
        if key not in self.storage:
            return None
        
        if not isinstance(self.storage[key], list):
            return Exception("Operation against a key holding the wrong kind of value")
        
        if len(self.storage[key]) == 0:
            return None
        
        return self.storage[key].pop(0)
    
    def handle_rpop(self, args):
        if len(args) != 1:
            return Exception("Wrong number of arguments for RPOP")
        
        key = args[0]
        if key not in self.storage:
            return None
        
        if not isinstance(self.storage[key], list):
            return Exception("Operation against a key holding the wrong kind of value")
        
        if len(self.storage[key]) == 0:
            return None
        
        return self.storage[key].pop()
    
    def handle_llen(self, args):
        if len(args) != 1:
            return Exception("Wrong number of arguments for LLEN")
        
        key = args[0]
        if key not in self.storage:
            return 0
        
        if not isinstance(self.storage[key], list):
            return Exception("Operation against a key holding the wrong kind of value")
        
        return len(self.storage[key])
    
    def handle_lrange(self, args):
        if len(args) != 3:
            return Exception("Wrong number of arguments for LRANGE")
        
        key = args[0]
        try:
            start = int(args[1])
            stop = int(args[2])
        except ValueError:
            return Exception("Value is not an integer")
        
        if key not in self.storage:
            return []
        
        if not isinstance(self.storage[key], list):
            return Exception("Operation against a key holding the wrong kind of value")
        
        # Convert negative indices and handle Redis's inclusive stop
        lst = self.storage[key]
        if start < 0:
            start = len(lst) + start
        if stop < 0:
            stop = len(lst) + stop
        
        # Redis LRANGE is inclusive of stop
        return lst[start:stop + 1]


if __name__ == "__main__":
    server = RedisServer()
    server.start()