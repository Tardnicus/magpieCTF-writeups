import socket
import sys


def main(argv):
    # Argument checking
    if len(argv) < 1:
        print("You must provide the host as an argument!", file = sys.stderr)
        return

    # Host grabbed from CLI argument, port is the same for all 3 vaults
    host = argv[0]
    port = 5555
    buffer_size = 4096

    # Open a TCP socket and resolve the IPof the host we got from the CLI
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        ip = socket.gethostbyname(host)

        # Establish the connection (3-way handshake)
        s.connect((ip, port))

        # First attempt (introduces extra overhead)
        # s.sendall(b"INITIALIZE CONNECTION\n")
        # s.sendall(b"SEND FLAG\n")

        # Send both commands IMMEDIATELY, not caring whether there is data to read or not
        # bundle them both together to avoid extra overhead from sendall() being called twice
        s.sendall(b"INITIALIZE CONNECTION\nSEND FLAG\n")

        # get_challenge extracts the challenge string from the data the server sent us, and we just send it right back (part of protocol)
        s.sendall(get_challenge(buffer_size, s))

        # Read the response from the server after replying with the challenge string (hopefully we were quick enough!)
        res = get_response(buffer_size, s)
        print(res)


def get_challenge(buffer_size, s) -> bytes:
    """Continues to read data from the socket, until we recognize the challenge string."""
    server_data = b''

    while True:

        # recv() blocks if there is no more data left to read, and the socket is still open
        server_data += s.recv(buffer_size)

        # First attempt (re library **might** not be as performant as string slicing)
        # match = re.findall(b'challenge string (.{7}\\n)', server_data)
        # if match:
        #     return match[0]

        # This is very hardcoded, but that's fine because we're just trying to break THIS protocol.
        # Sample bytestring: b'...with challenge string Z6D0N38\n' (remember, the `\n` is one character!)
        # They all have the same structure so if we check a slice of the output and get "str", we know that:
        # - We've read everything that the server has to send
        # - Our next command will be aligned properly
        if server_data[-15:-12] == b'str':
            # Remember requests NEED to have a \n at the end to be considered "submitted", so we include that.
            # i.e. 7 chars for the challenge, + 1 for the \n.
            return server_data[-8:]


def get_response(buffer_size, s):
    """Gets the final response from the server, assuming the rest of the protocol executed correctly."""
    server_data = b''

    try:
        while True:

            # Keep reading data until a \n. Honestly this is a pretty flaky solution because there are 7 \n's in a successful final string, but the chances of a buffered read with a 4096 byte buffer ending on one of those intermediate ones is quite low, at least experimentally.
            # If you run into problems, either remove it and ^C it yourself, OR use something like socket.select(). This worked for me, though.
            server_data += s.recv(buffer_size)
            if not server_data or server_data[-1] == ord(b'\n'):
                break

        return server_data

    # In case something happens that causes us to block waiting for more data (can sometimes happen), a ^C will print what we captured already
    except KeyboardInterrupt:
        return server_data


if __name__ == '__main__':
    # Removes program name from sysargs
    main(sys.argv[1:])
