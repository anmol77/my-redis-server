class RESPParser:
    def __init__(self):
        self.buffer = b""
    
    def feed(self, data):
        """Add data to the buffer"""
        self.buffer += data
    
    def parse_message(self):
        """Parse a single RESP message from the buffer"""
        if not self.buffer or len(self.buffer) == 0:
            return None
            
        # Get the first character to determine the type
        first_char = chr(self.buffer[0])
        
        if first_char == '*':
            return self._parse_array()
        elif first_char == '$':
            return self._parse_bulk_string()
        elif first_char == '+':
            return self._parse_simple_string()
        elif first_char == '-':
            return self._parse_error()
        elif first_char == ':':
            return self._parse_integer()
        else:
            raise ValueError(f"Invalid RESP type: {first_char}")
    
    def _parse_array(self):
        """Parse RESP array"""
        # Find the end of the line
        line_end = self.buffer.find(b'\r\n')
        if line_end == -1:
            return None
        
        # Parse the array length
        array_length = int(self.buffer[1:line_end])
        self.buffer = self.buffer[line_end + 2:]
        
        # Parse each element
        elements = []
        for _ in range(array_length):
            element = self.parse_message()
            if element is None:
                return None  # Not enough data
            elements.append(element)
        
        return elements
    
    def _parse_bulk_string(self):
        """Parse RESP bulk string"""
        line_end = self.buffer.find(b'\r\n')
        if line_end == -1:
            return None
        
        # Parse the string length
        string_length = int(self.buffer[1:line_end])
        self.buffer = self.buffer[line_end + 2:]
        
        # Check for null bulk string
        if string_length == -1:
            return None
        
        # Check if we have enough data
        if len(self.buffer) < string_length + 2:
            return None
        
        # Extract the string
        string_data = self.buffer[:string_length]
        self.buffer = self.buffer[string_length + 2:]  # Skip the \r\n
        
        return string_data.decode('utf-8')
    
    def _parse_simple_string(self):
        """Parse RESP simple string"""
        line_end = self.buffer.find(b'\r\n')
        if line_end == -1:
            return None
        
        string_data = self.buffer[1:line_end]
        self.buffer = self.buffer[line_end + 2:]
        
        return string_data.decode('utf-8')
    
    def _parse_error(self):
        """Parse RESP error"""
        line_end = self.buffer.find(b'\r\n')
        if line_end == -1:
            return None
        
        error_data = self.buffer[1:line_end]
        self.buffer = self.buffer[line_end + 2:]
        
        return Exception(error_data.decode('utf-8'))
    
    def _parse_integer(self):
        """Parse RESP integer"""
        line_end = self.buffer.find(b'\r\n')
        if line_end == -1:
            return None
        
        integer_data = int(self.buffer[1:line_end])
        self.buffer = self.buffer[line_end + 2:]
        
        return integer_data