class RESPEncoder:
    @staticmethod
    def encode(data):
        """Encode Python data to RESP format"""
        if isinstance(data, str):
            # Simple string
            return f"+{data}\r\n".encode('utf-8')
        elif isinstance(data, Exception):
            # Error
            return f"-{str(data)}\r\n".encode('utf-8')
        elif isinstance(data, int):
            # Integer
            return f":{data}\r\n".encode('utf-8')
        elif isinstance(data, bytes):
            # Bulk string - but we'll convert to regular bulk string format
            data_str = data.decode('utf-8')
            return f"${len(data_str)}\r\n{data_str}\r\n".encode('utf-8')
        elif data is None:
            # Null bulk string
            return b"$-1\r\n"
        elif isinstance(data, list):
            # Array
            encoded = f"*{len(data)}\r\n".encode('utf-8')
            for item in data:
                encoded += RESPEncoder.encode(item)
            return encoded
        else:
            # Convert to string by default
            str_data = str(data)
            return f"${len(str_data)}\r\n{str_data}\r\n".encode('utf-8')