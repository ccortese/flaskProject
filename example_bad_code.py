"""
Example file with intentional code issues to demonstrate the review agent
"""

# Hardcoded secret (ERROR)
api_key = "sk-1234567890abcdefghijklmnopqrstuvwxyz"
password = "mypassword123"

# Function without error handling (WARNING)
def saveUserData(userData):
    db.session.add(userData)
    db.session.commit()
    return userData.id

# Very long function (WARNING)
def processLargeDataSet(data):
    result = []
    for item in data:
        if item.type == 'A':
            processed = item.value * 2
        elif item.type == 'B':
            processed = item.value * 3
        elif item.type == 'C':
            processed = item.value * 4
        elif item.type == 'D':
            processed = item.value * 5
        elif item.type == 'E':
            processed = item.value * 6
        elif item.type == 'F':
            processed = item.value * 7
        elif item.type == 'G':
            processed = item.value * 8
        elif item.type == 'H':
            processed = item.value * 9
        elif item.type == 'I':
            processed = item.value * 10
        elif item.type == 'J':
            processed = item.value * 11
        elif item.type == 'K':
            processed = item.value * 12
        elif item.type == 'L':
            processed = item.value * 13
        elif item.type == 'M':
            processed = item.value * 14
        elif item.type == 'N':
            processed = item.value * 15
        elif item.type == 'O':
            processed = item.value * 16
        elif item.type == 'P':
            processed = item.value * 17
        elif item.type == 'Q':
            processed = item.value * 18
        elif item.type == 'R':
            processed = item.value * 19
        elif item.type == 'S':
            processed = item.value * 20
        elif item.type == 'T':
            processed = item.value * 21
        elif item.type == 'U':
            processed = item.value * 22
        elif item.type == 'V':
            processed = item.value * 23
        elif item.type == 'W':
            processed = item.value * 24
        elif item.type == 'X':
            processed = item.value * 25
        elif item.type == 'Y':
            processed = item.value * 26
        elif item.type == 'Z':
            processed = item.value * 27
        else:
            processed = item.value
        result.append(processed)
    return result

# Function without docstring (INFO)
def calculateTotal(items):
    total = 0
    for item in items:
        total += item.price
    return total

# Bad naming conventions (INFO)
def getUserData():
    userName = "john"
    userAge = 25
    return userName, userAge
