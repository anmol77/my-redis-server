Here I tried creating my own-redis-server.
Redis Uses a RESP(Redis Serialization Protocol) for client-server communication.

# What happens in the Redis server:

### 1. Raw data comes in from the network
<pre>raw_data = b"*2\r\n$3\r\nGET\r\n$5\r\nmykey\r\n" </pre>

### 2. RESP Parser converts it to Python data structures
<pre>parsed_command = ["GET", "mykey"]  # What the parser produces</pre>

### 3. Server processes the command using Python
<pre>result = storage.get("mykey")  # Returns "Hello"</pre>

### 4. RESP Encoder converts Python back to RESP format
<pre>encoded_response = b"$5\r\nHello\r\n"  # What the encoder produces</pre>

### 5. Send back to client
<pre>client_socket.send(encoded_response)</pre>

## Visual Flow
<pre> Network bytes → RESP Parser → Python objects → Command processing ↓ Network bytes ← RESP Encoder ← Python objects ← Command result  </pre>
