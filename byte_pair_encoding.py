#!/usr/bin/env python3
"""
Byte Pair Encoding Tokenizer for Indian Languages
A simple implementation of BPE tokenizer with Marathi-specific preprocessing.
Author: Shilpaj Bhalerao
Date: 2025-01-05
"""
# Standard Library Imports
import re

# Third Party Imports
from tqdm import tqdm


class BPETokenizer:
    """
    Byte Pair Encoding Tokenizer
    
    :param vocab_size (int): Size of final vocabulary (including base bytes)
    :param merges (dict): Dictionary of merge rules
    :param vocab (dict): Dictionary mapping token IDs to their byte sequences
    :param inverse_vocab (dict): Dictionary mapping byte sequences to token IDs
    """
    
    def __init__(self, vocab_size=1000, use_regex=False):
        """
        Initialize the tokenizer with desired vocabulary size.
        """
        self.vocab_size = vocab_size
        self.merges = {}
        self.len_of_ids = 0
        self.len_raw_bytes = 0
        self.vocab = {idx: bytes([idx]) for idx in range(256)}
        self.inverse_vocab = {bytes([idx]): idx for idx in range(256)}
        self.use_regex = use_regex
        
        # Marathi tokenization regex pattern
        self.marathi_regex = re.compile(
            r"([\u0900-\u094F\u0951-\u097F]+|"           # Marathi words and ligatures
            r"[\u0966-\u096F]+|"                         # Marathi numerals (०-९)
            r"\d+(?:\s[\u0900-\u097F]+)?|"              # Arabic numerals with Marathi context
            r"#[\w\u0900-\u097F]+|"                     # Hashtags
            r"[\w\u0900-\u097F]+[''][\w\u0900-\u097F]+|" # Compound words with apostrophes
            r"[\w\u0900-\u097F]+(?:-[\w\u0900-\u097F]+)*|" # Hyphenated words
            r"[\w\u0900-\u097F]+\.[\w\u0900-\u097F]*|"  # Abbreviations
            r'\"[^\"]+\"|\'[^\']+\'|'                   # Quoted text
            r"[\u0964\u0965.!?…]|"                      # Marathi punctuation
            r"[^\s\u0900-\u097F]+)"                     # Non-Marathi symbols
        )
    
    def preprocess(self, text: str) -> str:
        """
        Preprocess Marathi text before tokenization.
        
        :param text: Input Marathi text
        :return: Preprocessed text with tokens separated by spaces
        """
        # Find all tokens using the Marathi regex
        tokens = self.marathi_regex.findall(text)
        
        # Join tokens with spaces
        processed_text = ' '.join(tokens)
        
        # Normalize whitespace
        processed_text = ' '.join(processed_text.split())
        
        return processed_text
    
    def _get_stats(self, ids: list[int]) -> dict[tuple[int, int], int]:
        """
        Count frequency of adjacent pairs in sequence.
        
        :param ids: list of integers
        :return: dictionary of pairs and their frequencies
        """
        counts = {}
        for pair in zip(ids, ids[1:]):
            counts[pair] = counts.get(pair, 0) + 1
        return counts
    
    def _merge(self, ids: list[int], pair: tuple[int, int], idx: int) -> list[int]:
        """
        Replace all occurrences of pair with new token idx.
        
        :param ids: list of integers
        :param pair: tuple of integers
        :param idx: integer
        :return: list of integers
        """
        newids = []
        i = 0
        while i < len(ids):
            if i < len(ids) - 1 and ids[i] == pair[0] and ids[i+1] == pair[1]:
                newids.append(idx)
                i += 2
            else:
                newids.append(ids[i])
                i += 1
        return newids
    
    def train(self, text: str):
        """
        Train the BPE tokenizer on the given text.
        :param text: Input text to train on
        """
        print("Training BPE tokenizer...")

        # Preprocess text first
        if self.use_regex:
            text = self.preprocess(text)
        
        # Convert text to bytes and get initial tokens
        raw_bytes = text.encode("utf-8")
        raw_bytes = list(map(int, raw_bytes))  # convert to integers
        self.len_raw_bytes = len(raw_bytes)
        
        # Calculate number of merges needed
        num_merges = self.vocab_size - 256
        ids = list(raw_bytes)  # copy so we don't destroy the original list
        
        # Perform merges
        for i in tqdm(range(num_merges)):
            stats = self._get_stats(ids)
            if not stats:
                break
                
            # Find most frequent pair
            pair = max(stats, key=stats.get)
            idx = 256 + i
            
            # Perform the merge
            ids = self._merge(ids, pair, idx)
            self.len_of_ids = len(ids)
            self.merges[pair] = idx
            
            # Update vocabulary
            new_token = self.vocab[pair[0]] + self.vocab[pair[1]]
            self.vocab[idx] = new_token
            self.inverse_vocab[new_token] = idx
    
    def encode(self, text: str) -> list[int]:
        """
        Encode text into token IDs.
        
        :param text: Text to encode
        :return: List of token IDs
        """
        # Preprocess if needed
        if self.use_regex:
            text = self.preprocess(text)
        
        # Convert text to list of integers
        tokens = list(text.encode("utf-8"))
        while len(tokens) >= 2:
            stats = self._get_stats(tokens)
            pair = min(stats, key=lambda p: self.merges.get(p, float("inf")))
            if pair not in self.merges:
                break # nothing else can be merged
            idx = self.merges[pair]
            tokens = self._merge(tokens, pair, idx)
        return tokens
    
    def decode(self, ids: list[int]) -> str:
        """
        Decode token IDs back to text.
        
        :param ids: List of token IDs
        :return: Decoded text
        """
        tokens = b"".join(self.vocab[idx] for idx in ids)
        return tokens.decode("utf-8", errors="replace")
    
    def token_to_text(self, token_id: int) -> str:
        """
        Convert a single token ID to its text representation.
        
        :param token_id: Token ID
        :return: Text representation of the token
        """
        return self.vocab[token_id].decode("utf-8", errors="replace")
    
    def save(self, path: str):
        """
        Save tokenizer state to file.
        
        :param path: Path to save the file
        """
        import json
        state = {
            'vocab_size': self.vocab_size,
            'merges': list(self.merges.items()),  # Convert to list of tuples
            'vocab': {k: list(v) for k, v in self.vocab.items()}  # Convert bytes to lists
        }
        with open(path, 'w') as f:
            json.dump(state, f)
    
    @classmethod
    def load(cls, path: str):
        """
        Load tokenizer state from file.
        
        :param path: Path to load the file
        :return: Loaded tokenizer
        """
        import json
        with open(path, 'r') as f:
            state = json.load(f)
        
        tokenizer = cls(vocab_size=state['vocab_size'])
        # Convert lists back to tuples for the merge pairs
        tokenizer.merges = {tuple(k): v for k, v in state['merges']}
        tokenizer.vocab = {int(k): bytes(v) for k, v in state['vocab'].items()}
        tokenizer.inverse_vocab = {v: k for k, v in tokenizer.vocab.items()}
        return tokenizer
    
    def get_vocab_size(self) -> int:
        """
        Get the size of the vocabulary.
        
        :return: Size of the vocabulary
        """
        return len(self.vocab)
    
    def get_compression_ratio(self, text: str) -> float:
        """
        Get the compression ratio of the text.
        
        :param text: Input text
        :return: Compression ratio (original_length / encoded_length)
        """
        # Preprocess if needed
        if self.use_regex:
            text = self.preprocess(text)
        
        return round(self.len_raw_bytes / self.len_of_ids, 4)

    def get_token_length(self, text: str) -> int:
        """
        Get the length of the tokenized text.
        
        :param text: Input text
        :return: Length of the tokenized text
        """
        return self.len_raw_bytes
    
    def get_ids_length(self, text: str) -> int:
        """
        Get the length of the tokenized text.
        
        :param text: Input text
        :return: Length of the tokenized text
        """
        return self.len_of_ids

    def is_encoded_equals_decoded(self, text: str) -> bool:
        """
        Check if encoding and decoding are consistent.
        
        :param text: Input text
        :return: True if consistent, False otherwise
        """
        encoded = self.encode(text)
        decoded = self.decode(encoded)
        return text == decoded


if __name__ == "__main__":

    # Read text from file
    with open("dataset.txt", "r") as file:
        text = file.read()

    # Initialize and train
    tokenizer = BPETokenizer(vocab_size=3000)
    tokenizer.train(text)

    # Save and load
    tokenizer.save("tokenizer.json")
    loaded_tokenizer = BPETokenizer.load("tokenizer.json")

    # Encode and decode
    encoded = tokenizer.encode("या पुतळ्याच्या डोक्यावर अज्ञातांनी चप्पल ठेवल्याचे आढळून आले आहे.")
    decoded = loaded_tokenizer.decode(encoded)

    # Check consistency
    print("Is encoded equals to loaded decoded? ", decoded == "या पुतळ्याच्या डोक्यावर अज्ञातांनी चप्पल ठेवल्याचे आढळून आले आहे.")

    # Print vocab size
    print(f"Vocab size: {tokenizer.get_vocab_size()}")

    # Print token length
    print(f"Token length: {tokenizer.get_token_length(text)}")

    # Print ids length
    print(f"Ids length: {tokenizer.get_ids_length(text)}")

    # Print compression ratio
    print(f"Compression ratio: {tokenizer.get_compression_ratio(text)}X")
