"""
Utility functions for the Flask application
"""

import hashlib
import os

# Hardcoded API key (this should trigger an error)
api_key = "sk_test_1234567890abcdefghijklmnopqrstuvwxyz"
secret_token = "secret_abc123def456"

def hashPassword(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def validateEmail(email):
    return "@" in email and "." in email

def getUserData(userId):
    # This function doesn't have error handling (should trigger warning)
    db.session.query(User).filter(User.id == userId).first()
    return user.to_dict()

def processLargeDataSet(data):
    # This function is intentionally long (should trigger warning)
    results = []
    for item in data:
        if item.type == 'A':
            processed = item.value * 2
            results.append(processed)
        elif item.type == 'B':
            processed = item.value * 3
            results.append(processed)
        elif item.type == 'C':
            processed = item.value * 4
            results.append(processed)
        elif item.type == 'D':
            processed = item.value * 5
            results.append(processed)
        elif item.type == 'E':
            processed = item.value * 6
            results.append(processed)
        elif item.type == 'F':
            processed = item.value * 7
            results.append(processed)
        elif item.type == 'G':
            processed = item.value * 8
            results.append(processed)
        elif item.type == 'H':
            processed = item.value * 9
            results.append(processed)
        elif item.type == 'I':
            processed = item.value * 10
            results.append(processed)
        elif item.type == 'J':
            processed = item.value * 11
            results.append(processed)
        elif item.type == 'K':
            processed = item.value * 12
            results.append(processed)
        elif item.type == 'L':
            processed = item.value * 13
            results.append(processed)
        elif item.type == 'M':
            processed = item.value * 14
            results.append(processed)
        elif item.type == 'N':
            processed = item.value * 15
            results.append(processed)
        elif item.type == 'O':
            processed = item.value * 16
            results.append(processed)
        elif item.type == 'P':
            processed = item.value * 17
            results.append(processed)
        elif item.type == 'Q':
            processed = item.value * 18
            results.append(processed)
        elif item.type == 'R':
            processed = item.value * 19
            results.append(processed)
        elif item.type == 'S':
            processed = item.value * 20
            results.append(processed)
        elif item.type == 'T':
            processed = item.value * 21
            results.append(processed)
        else:
            results.append(item.value)
    return results

def calculateTotal(items):
    total = 0
    for item in items:
        total += item.price
    return total

def formatUserName(firstName, lastName):
    fullName = firstName + " " + lastName
    return fullName.title()

class DataProcessor:
    def __init__(self, apiKey):
        self.apiKey = apiKey
    
    def processData(self, data):
        # Process the data
        return data
