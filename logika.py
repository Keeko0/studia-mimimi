import re
from collections import Counter

def is_palindrome(text: str) -> bool:
    cleaned_text = text.replace(" ", "").lower()
    return cleaned_text == cleaned_text[::-1]

def fibonacci(n: int) -> int:
    if n < 0:
        raise ValueError("n musi być liczbą nieujemną")
    if n == 0:
        return 0
    
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    
    return b

def count_vowels(text: str) -> int:
    VOWELS = "aeiouy"
    count = 0
    for char in text.lower():
        if char in VOWELS:
            count += 1
    return count

def calculate_discount(price: float, discount: float) -> float:
    if not 0 <= discount <= 1:
        raise ValueError("Zniżka musi być w zakresie od 0 do 1")
    return price * (1 - discount)

def flatten_list(nested_list: list) -> list:
    flat = []
    for item in nested_list:
        if isinstance(item, list):
            flat.extend(flatten_list(item))
        else:
            flat.append(item)
    return flat

def word_frequencies(text: str) -> dict:
    cleaned_text = re.sub(r'[^\w\s]', '', text).lower()
    words = cleaned_text.split()
    
    return dict(Counter(words))

def is_prime(n: int) -> bool:
    if n < 2:
        return False
    
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
            
    return True