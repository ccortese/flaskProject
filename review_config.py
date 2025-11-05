"""
Configuration for the PR Review Agent

This file contains settings and customization options for the automated code review.
"""

# Review Check Configuration
REVIEW_CHECKS = {
    'hardcoded_secrets': {
        'enabled': True,
        'severity': 'error',
        'patterns': [
            (r'api_key\s*=\s*["\'][^"\']{10,}["\']', 'API key'),
            (r'password\s*=\s*["\'][^"\']{3,}["\']', 'Password'),
            (r'secret\s*=\s*["\'][^"\']{10,}["\']', 'Secret'),
            (r'token\s*=\s*["\'][^"\']{10,}["\']', 'Token'),
            (r'key\s*=\s*["\'][^"\']{20,}["\']', 'Key'),
        ],
        'exclude_patterns': [
            r'os\.getenv',
            r'os\.environ',
            r'config\.',
            r'#.*',  # Comments
        ]
    },
    
    'error_handling': {
        'enabled': True,
        'severity': 'warning',
        'risky_operations': [
            'db.session',
            'open(',
            'requests.',
            'json.loads',
            'int(',
            'float(',
            'urllib.',
        ]
    },
    
    'function_length': {
        'enabled': True,
        'severity': 'warning',
        'max_lines': 50,
        'exclude_functions': [
            '__init__',
            'main',
        ]
    },
    
    'documentation': {
        'enabled': True,
        'severity': 'info',
        'min_function_lines': 3,
        'exclude_private': True,  # Skip functions starting with _
        'exclude_short': True,   # Skip very short functions
    },
    
    'naming_conventions': {
        'enabled': True,
        'severity': 'info',
        'function_pattern': r'^[a-z][a-z0-9_]*$',
        'variable_pattern': r'^[a-z][a-z0-9_]*$',
        'constant_pattern': r'^[A-Z][A-Z0-9_]*$',
        'exclude_magic': True,  # Skip __magic__ methods
    }
}

# File Exclusions
EXCLUDE_FILES = [
    '__pycache__',
    '.git',
    'venv',
    'env',
    '.pytest_cache',
    'node_modules',
]

EXCLUDE_FILE_PATTERNS = [
    r'.*test.*\.py$',      # Test files
    r'.*_test\.py$',       # Test files
    r'migrations/.*\.py$', # Database migrations
    r'setup\.py$',         # Setup files
]

# GitHub Integration
GITHUB_CONFIG = {
    'comment_header': '# 🤖 Automated Code Review',
    'success_message': '✅ All checks passed!',
    'failure_message': '❌ Issues found that need attention',
    'post_success_comments': False,  # Only comment when issues found
}

# Output Formatting
OUTPUT_CONFIG = {
    'show_suggestions': True,
    'group_by_severity': True,
    'include_line_numbers': True,
    'max_violations_per_file': 20,  # Limit output for very problematic files
}

# Severity Levels
SEVERITY_LEVELS = {
    'error': {
        'emoji': '❌',
        'title': 'Errors (Must Fix)',
        'description': 'These issues must be resolved before merging'
    },
    'warning': {
        'emoji': '⚠️',
        'title': 'Warnings (Should Fix)',
        'description': 'These issues are strongly recommended to fix'
    },
    'info': {
        'emoji': 'ℹ️',
        'title': 'Suggestions (Nice to Have)',
        'description': 'These are suggestions for improvement'
    }
}
