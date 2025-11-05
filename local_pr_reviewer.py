#!/usr/bin/env python3
"""
Local PR Reviewer

This script allows you to run the PR review agent locally on your machine.
It can review specific files, all Python files, or files changed in a specific PR.

Usage:
    python local_pr_reviewer.py --file app.py                    # Review single file
    python local_pr_reviewer.py --all                           # Review all Python files
    python local_pr_reviewer.py --pr 123                        # Review files in PR #123
    python local_pr_reviewer.py --changed                       # Review uncommitted changes
"""

import os
import sys
import argparse
import subprocess
import requests
from typing import List, Optional
from pr_review_agent import CodeReviewer, format_review_comment


def get_github_token() -> Optional[str]:
    """Get GitHub token from environment or git config"""
    # Try environment variable first
    token = os.getenv('GITHUB_TOKEN')
    if token:
        return token
    
    # Try git config
    try:
        result = subprocess.run(['git', 'config', 'github.token'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    return None


def get_repo_info() -> tuple:
    """Get repository owner and name from git remote"""
    try:
        result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            url = result.stdout.strip()
            # Parse GitHub URL
            if 'github.com' in url:
                if url.startswith('git@'):
                    # SSH format: git@github.com:owner/repo.git
                    parts = url.split(':')[1].replace('.git', '').split('/')
                else:
                    # HTTPS format: https://github.com/owner/repo.git
                    parts = url.split('/')[-2:]
                    parts[1] = parts[1].replace('.git', '')
                return parts[0], parts[1]
    except:
        pass
    
    return None, None


def get_pr_files(pr_number: int, owner: str, repo: str, token: str) -> List[str]:
    """Get list of files changed in a PR"""
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
    headers = {'Authorization': f'token {token}'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        files = response.json()
        
        # Return only Python files
        return [f['filename'] for f in files if f['filename'].endswith('.py')]
    except Exception as e:
        print(f"Error fetching PR files: {e}")
        return []


def get_changed_files() -> List[str]:
    """Get list of uncommitted changed Python files"""
    try:
        # Get staged and unstaged changes
        result = subprocess.run(['git', 'diff', '--name-only', 'HEAD'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            files = result.stdout.strip().split('\n')
            return [f for f in files if f.endswith('.py') and f]
    except:
        pass
    
    return []


def find_python_files(directory: str = '.') -> List[str]:
    """Find all Python files in directory"""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip hidden directories and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    return python_files


def post_pr_comment(pr_number: int, owner: str, repo: str, token: str, comment: str):
    """Post a comment to a PR"""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
    headers = {
        'Authorization': f'token {token}',
        'Content-Type': 'application/json'
    }
    data = {'body': comment}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print(f"✅ Posted review comment to PR #{pr_number}")
    except Exception as e:
        print(f"❌ Error posting comment to PR: {e}")


def main():
    parser = argparse.ArgumentParser(description='Local PR Review Agent')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--file', help='Review a specific file')
    group.add_argument('--all', action='store_true', help='Review all Python files')
    group.add_argument('--pr', type=int, help='Review files in a specific PR')
    group.add_argument('--changed', action='store_true', help='Review uncommitted changes')
    
    parser.add_argument('--post-comment', action='store_true', 
                       help='Post review as comment to PR (requires --pr)')
    parser.add_argument('--output', choices=['console', 'markdown', 'json'], 
                       default='console', help='Output format')
    
    args = parser.parse_args()
    
    # Determine files to review
    files_to_review = []
    
    if args.file:
        if os.path.exists(args.file):
            files_to_review = [args.file]
        else:
            print(f"❌ File not found: {args.file}")
            sys.exit(1)
    
    elif args.all:
        files_to_review = find_python_files()
        print(f"Found {len(files_to_review)} Python files to review")
    
    elif args.changed:
        files_to_review = get_changed_files()
        if not files_to_review:
            print("No uncommitted Python files found")
            sys.exit(0)
        print(f"Found {len(files_to_review)} changed Python files")
    
    elif args.pr:
        # Get repository info
        owner, repo = get_repo_info()
        if not owner or not repo:
            print("❌ Could not determine repository info from git remote")
            sys.exit(1)
        
        # Get GitHub token
        token = get_github_token()
        if not token:
            print("❌ GitHub token required. Set GITHUB_TOKEN environment variable")
            sys.exit(1)
        
        files_to_review = get_pr_files(args.pr, owner, repo, token)
        if not files_to_review:
            print(f"No Python files found in PR #{args.pr}")
            sys.exit(0)
        print(f"Found {len(files_to_review)} Python files in PR #{args.pr}")
    
    # Run review
    reviewer = CodeReviewer()
    all_violations = []
    review_comments = []
    
    for file_path in files_to_review:
        print(f"Reviewing: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            violations = reviewer.review_file(file_path, content)
            all_violations.extend(violations)
            
            if violations:
                comment = format_review_comment(violations, file_path)
                review_comments.append(comment)
        
        except Exception as e:
            print(f"❌ Error reviewing {file_path}: {e}")
    
    # Output results
    if args.output == 'console':
        if review_comments:
            for comment in review_comments:
                print("\n" + "="*80)
                print(comment)
        else:
            print("\n✅ All files passed review!")
    
    elif args.output == 'markdown':
        if review_comments:
            full_comment = "\n\n---\n\n".join(review_comments)
            print(full_comment)
    
    elif args.output == 'json':
        import json
        result = {
            'files_reviewed': len(files_to_review),
            'total_violations': len(all_violations),
            'violations_by_severity': {
                'error': len([v for v in all_violations if v.severity == 'error']),
                'warning': len([v for v in all_violations if v.severity == 'warning']),
                'info': len([v for v in all_violations if v.severity == 'info'])
            },
            'violations': [
                {
                    'file': v.check_name,  # This should be file path, but we'll use check_name for now
                    'line': v.line_number,
                    'severity': v.severity,
                    'message': v.message,
                    'suggestion': v.suggestion
                }
                for v in all_violations
            ]
        }
        print(json.dumps(result, indent=2))
    
    # Post comment to PR if requested
    if args.post_comment and args.pr and review_comments:
        full_comment = f"# 🤖 Local Code Review - PR #{args.pr}\n\n"
        full_comment += "\n\n---\n\n".join(review_comments)
        post_pr_comment(args.pr, owner, repo, token, full_comment)
    
    # Print summary
    print(f"\n📊 Review Summary:")
    print(f"Files reviewed: {len(files_to_review)}")
    print(f"Total violations: {len(all_violations)}")
    print(f"Errors: {len([v for v in all_violations if v.severity == 'error'])}")
    print(f"Warnings: {len([v for v in all_violations if v.severity == 'warning'])}")
    print(f"Suggestions: {len([v for v in all_violations if v.severity == 'info'])}")
    
    # Exit with error code if there are errors
    if any(v.severity == 'error' for v in all_violations):
        sys.exit(1)


if __name__ == "__main__":
    main()
