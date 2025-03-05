import sys, os, base64

def main():
    if len(sys.argv) < 2:
        sys.exit("Nutzung: python to_base64.py <input_file>")
    infile = sys.argv[1]
    try:
        with open(infile, "r") as f:
            data = f.readlines()
    except Exception as e:
        sys.exit(str(e))
    byte_data = bytearray()
    for line in data:
        parts = line.strip().split()
        if len(parts) != 3:
            sys.exit("Error: Each line must contain exactly three numbers.")
        try:
            nums = [int(x) for x in parts]
        except Exception as e:
            sys.exit("Error: Non-integer value encountered.")
        for num in nums:
            if not (0 <= num < 65536):
                sys.exit("Error: Number out of range (0 <= number < 65536).")
            byte_data += num.to_bytes(2, byteorder="big")
    b64_str = base64.b64encode(byte_data).decode("ascii")
    outfile = os.path.basename(infile) + ".base64.txt"
    try:
        with open(outfile, "w") as f:
            f.write(b64_str)
    except Exception as e:
        sys.exit(str(e))

if __name__ == "__main__":
    main()
