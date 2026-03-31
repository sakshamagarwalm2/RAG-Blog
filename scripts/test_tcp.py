import socket
import sys

def test_tcp_connection(host, port):
    print(f"Testing TCP connection to {host}:{port}...")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((host, port))
        print(f"SUCCESS: TCP connection successful to {host}:{port}")
        s.close()
        return True
    except Exception as e:
        print(f"FAILED: TCP connection failed to {host}:{port}: {e}")
        return False

if __name__ == "__main__":
    # Test all MongoDB shards
    shards = [
        'ac-ebua8tu-shard-00-00.zioyfty.mongodb.net',
        'ac-ebua8tu-shard-00-01.zioyfty.mongodb.net',
        'ac-ebua8tu-shard-00-02.zioyfty.mongodb.net'
    ]
    
    all_success = True
    for shard in shards:
        if not test_tcp_connection(shard, 27017):
            all_success = False
    
    if all_success:
        print("\nSUCCESS: All MongoDB shards are reachable via TCP")
    else:
        print("\nFAILED: Some MongoDB shards are not reachable")
        sys.exit(1)