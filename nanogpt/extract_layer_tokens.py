from vocabulary import Vocabulary
import json

def main():
    vocab = Vocabulary.load("german-complete.vocab")
    results = []
    for token in vocab.tokens:
        results.append(str(token))
    with open("/tmp/temp.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    main()
