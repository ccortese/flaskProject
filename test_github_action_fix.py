#!/usr/bin/env python3
"""
Test file to verify GitHub Action PR review system is working correctly.

This file contains some intentional code issues to test the review system:
1. A function that's too long
2. Missing error handling
3. Hardcoded values that should be configurable
"""

import os
import sys


def test_function_with_issues():
    """
    This function has several issues that should be caught by the PR review system.
    """
    # Issue 1: Hardcoded API key (should be flagged as security issue)
    api_key = "sk-1234567890abcdef"
    
    # Issue 2: Missing error handling for file operations
    with open("test_file.txt", "r") as f:
        content = f.read()
    
    # Issue 3: Function is getting too long (this is intentional for testing)
    result = []
    for i in range(100):
        if i % 2 == 0:
            result.append(i * 2)
        else:
            result.append(i * 3)
    
    # Issue 4: Using print instead of proper logging
    print(f"Processing {len(result)} items")
    
    # Issue 5: No docstring for complex logic
    processed_data = {}
    for item in result:
        if item not in processed_data:
            processed_data[item] = 1
        else:
            processed_data[item] += 1
    
    return processed_data


def good_function():
    """
    This function follows best practices and should pass review.
    
    Returns:
        str: A simple greeting message
    """
    try:
        message = "Hello, World!"
        return message
    except Exception as e:
        print(f"Error generating message: {e}")
        return "Default message"


if __name__ == "__main__":
    print("Testing GitHub Action PR review system...")
    result = test_function_with_issues()
    greeting = good_function()
    print(f"Result: {result}")
    print(f"Greeting: {greeting}")
