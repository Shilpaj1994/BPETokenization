#!/usr/bin/env python3
"""
Script to show tokens of the input text
"""
# Local Imports
from byte_pair_encoding import BPETokenizer


if __name__ == "__main__":
    tokenizer = BPETokenizer.load("tokenizer.json")
    text = "या पुतळ्याच्या डोक्यावर अज्ञातांनी चप्पल ठेवल्याचे आढळून आले आहे."
    # text = "સરળ ગુજરાતી બી પી ઇ ટોકનાઇઝર"
    encoded = tokenizer.encode(text)
    print(encoded)
    print(tokenizer.decode(encoded))


