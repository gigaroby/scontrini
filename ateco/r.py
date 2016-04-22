from pprint import pprint

def main():
    mapping = {}
    previous = ""
    with open('ateco-friendly.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            values = line.split(' ', 1)
            if len(values) == 1:
                assert previous != "", "error in the input file, the first ateco should have a friendly name"
                ateco, friendly = values[0], previous
            else:
                ateco, friendly  = values
                previous = friendly

            mapping[ateco] = friendly

    return mapping



if __name__ == '__main__':
    mapping = main()
    pprint(mapping)
    print("there are {} categories".format(len({x for _, x in mapping.items()})))

