#!/usr/bin/env python3
"""
Flask Project PR Review Agent

This script automatically reviews Python files in PRs against 5 coding standards:
1. No hardcoded secrets (API keys, passwords, tokens)
2. Proper error handling (try/except blocks)
3. Function length (max 50 lines)
4. Documentation (functions have docstrings)
5. Naming conventions (snake_case for functions/variables)
"""

import re
import ast
import os
import sys
import json
import argparse
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass


@dataclass
class ReviewViolation:
    """Represents a code review violation"""
    check_name: str
    severity: str  # 'error', 'warning', 'info'
    line_number: int
    message: str
    suggestion: str = ""


class CodeReviewer:
    """Main class for reviewing Python code against coding standards"""
    
    def __init__(self):
        self.violations = []
    
    def review_file(self, file_path: str, content: str) -> List[ReviewViolation]:
        """Review a single Python file and return violations"""
        self.violations = []
        
        # Skip non-Python files
        if not file_path.endswith('.py'):
            return self.violations
        
        # Run all checks
        self._check_hardcoded_secrets(content, file_path)
        self._check_error_handling(content, file_path)
        self._check_function_length(content, file_path)
        self._check_documentation(content, file_path)
        self._check_naming_conventions(content, file_path)
        
        return self.violations
    
    def _check_hardcoded_secrets(self, content: str, file_path: str):
        """Check for hardcoded secrets like API keys, passwords, tokens"""
        secret_patterns = [
            (r'api_key\s*=\s*["\'][^"\']{10,}["\']', 'API key'),
            (r'password\s*=\s*["\'][^"\']{3,}["\']', 'Password'),
            (r'secret\s*=\s*["\'][^"\']{10,}["\']', 'Secret'),
            (r'token\s*=\s*["\'][^"\']{10,}["\']', 'Token'),
            (r'key\s*=\s*["\'][^"\']{20,}["\']', 'Key'),
            (r'["\'][A-Za-z0-9]{32,}["\']', 'Potential secret string'),
        ]
        
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            # Skip comments and environment variable usage
            if line.strip().startswith('#') or 'os.getenv' in line or 'os.environ' in line:
                continue
                
            for pattern, secret_type in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self.violations.append(ReviewViolation(
                        check_name="hardcoded_secrets",
                        severity="error",
                        line_number=line_num,
                        message=f"Potential hardcoded {secret_type.lower()} detected",
                        suggestion="Use environment variables or config files for sensitive data"
                    ))
    
    def _check_error_handling(self, content: str, file_path: str):
        """Check for proper error handling in functions"""
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if function has any risky operations without try/except
                has_try_except = any(isinstance(child, ast.Try) for child in ast.walk(node))
                has_risky_ops = self._has_risky_operations(node)
                
                if has_risky_ops and not has_try_except:
                    self.violations.append(ReviewViolation(
                        check_name="error_handling",
                        severity="warning",
                        line_number=node.lineno,
                        message=f"Function '{node.name}' performs risky operations without error handling",
                        suggestion="Add try/except blocks around database operations, file I/O, or external API calls"
                    ))
    
    def _has_risky_operations(self, func_node: ast.FunctionDef) -> bool:
        """Check if function has operations that should be wrapped in try/except"""
        risky_patterns = [
            'db.session',  # Database operations
            'open(',       # File operations
            'requests.',   # HTTP requests
            'json.loads',  # JSON parsing
            'int(',        # Type conversions
            'float(',
        ]
        
        func_source = ast.unparse(func_node) if hasattr(ast, 'unparse') else str(func_node)
        return any(pattern in func_source for pattern in risky_patterns)
    
    def _check_function_length(self, content: str, file_path: str):
        """Check that functions are not too long (max 50 lines)"""
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Calculate function length
                if hasattr(node, 'end_lineno'):
                    func_length = node.end_lineno - node.lineno + 1
                else:
                    # Fallback for older Python versions
                    func_length = len([n for n in ast.walk(node) if hasattr(n, 'lineno')])
                
                if func_length > 50:
                    self.violations.append(ReviewViolation(
                        check_name="function_length",
                        severity="warning",
                        line_number=node.lineno,
                        message=f"Function '{node.name}' is {func_length} lines long (max 50 recommended)",
                        suggestion="Consider breaking this function into smaller, more focused functions"
                    ))
    
    def _check_documentation(self, content: str, file_path: str):
        """Check that functions have docstrings"""
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip private functions and very short functions
                if node.name.startswith('_') or len(node.body) < 3:
                    continue
                
                # Check if function has a docstring
                has_docstring = (
                    node.body and
                    isinstance(node.body[0], ast.Expr) and
                    isinstance(node.body[0].value, ast.Constant) and
                    isinstance(node.body[0].value.value, str)
                )
                
                if not has_docstring:
                    self.violations.append(ReviewViolation(
                        check_name="documentation",
                        severity="info",
                        line_number=node.lineno,
                        message=f"Function '{node.name}' is missing a docstring",
                        suggestion="Add a docstring describing what the function does, its parameters, and return value"
                    ))
    
    def _check_naming_conventions(self, content: str, file_path: str):
        """Check that functions and variables use snake_case naming"""
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return
        
        for node in ast.walk(tree):
            # Check function names
            if isinstance(node, ast.FunctionDef):
                if not self._is_snake_case(node.name) and not node.name.startswith('__'):
                    self.violations.append(ReviewViolation(
                        check_name="naming_conventions",
                        severity="info",
                        line_number=node.lineno,
                        message=f"Function '{node.name}' should use snake_case naming",
                        suggestion="Rename to follow snake_case convention (e.g., 'my_function')"
                    ))
            
            # Check variable assignments
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if not self._is_snake_case(target.id) and not target.id.isupper():
                            self.violations.append(ReviewViolation(
                                check_name="naming_conventions",
                                severity="info",
                                line_number=node.lineno,
                                message=f"Variable '{target.id}' should use snake_case naming",
                                suggestion="Use snake_case for variables (e.g., 'my_variable') or UPPER_CASE for constants"
                            ))
    
    def _is_snake_case(self, name: str) -> bool:
        """Check if a name follows snake_case convention"""
        return re.match(r'^[a-z][a-z0-9_]*$', name) is not None


def format_review_comment(violations: List[ReviewViolation], file_path: str) -> str:
    """Format violations into a GitHub comment"""
    if not violations:
        return f"✅ **{file_path}**: All checks passed!"
    
    comment = f"## 🔍 Code Review for `{file_path}`\n\n"
    
    # Group violations by severity
    errors = [v for v in violations if v.severity == 'error']
    warnings = [v for v in violations if v.severity == 'warning']
    info = [v for v in violations if v.severity == 'info']
    
    if errors:
        comment += "### ❌ Errors (Must Fix)\n"
        for violation in errors:
            comment += f"- **Line {violation.line_number}**: {violation.message}\n"
            if violation.suggestion:
                comment += f"  💡 *{violation.suggestion}*\n"
        comment += "\n"
    
    if warnings:
        comment += "### ⚠️ Warnings (Should Fix)\n"
        for violation in warnings:
            comment += f"- **Line {violation.line_number}**: {violation.message}\n"
            if violation.suggestion:
                comment += f"  💡 *{violation.suggestion}*\n"
        comment += "\n"
    
    if info:
        comment += "### ℹ️ Suggestions (Nice to Have)\n"
        for violation in info:
            comment += f"- **Line {violation.line_number}**: {violation.message}\n"
            if violation.suggestion:
                comment += f"  💡 *{violation.suggestion}*\n"
        comment += "\n"
    
    return comment


if __name__ == "__main__":
    # Simple test when run directly
    reviewer = CodeReviewer()
    
    # Test with the current app.py file
    if os.path.exists('app.py'):
        with open('app.py', 'r') as f:
            content = f.read()
        
        violations = reviewer.review_file('app.py', content)
        comment = format_review_comment(violations, 'app.py')
        print(comment)
    else:
        print("No app.py file found to review")
