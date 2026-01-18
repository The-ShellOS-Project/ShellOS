import sys

def echo():
    if len(sys.argv) > 1:
        print(" ".join(sys.argv[1:]))
    else:
        print("Usage: python script.py [message]")

if __name__ == "__main__":
    echo()
