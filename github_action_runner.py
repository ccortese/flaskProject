#!/usr/bin/env python3
"""
GitHub Action Runner for PR Review Agent

This script is called by the GitHub Action to review changed files in a PR.
It reads the changed files, runs the review agent, and outputs results for the action.
"""

import os
import sys
import argparse
import json
from typing import List
from pr_review_agent import CodeReviewer, format_review_comment


def main():
    parser = argparse.ArgumentParser(description='Run PR code review')
    parser.add_argument('--pr-number', required=True, help='PR number')
    parser.add_argument('--repo', required=True, help='Repository name (owner/repo)')
    parser.add_argument('--changed-files', required=True, help='File containing list of changed files')
    
    args = parser.parse_args()
    
    # Read changed files
    changed_files = []
    try:
        with open(args.changed_files, 'r') as f:
            changed_files = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("No changed files found")
        return
    
    if not changed_files:
        print("No Python files changed in this PR")
        return
    
    print(f"Reviewing {len(changed_files)} changed Python files...")
    
    reviewer = CodeReviewer()
    all_violations = []
    review_comments = []
    has_errors = False
    
    # Review each changed file
    for file_path in changed_files:
        if not file_path.endswith('.py'):
            continue
            
        print(f"Reviewing: {file_path}")
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Run review
            violations = reviewer.review_file(file_path, content)
            all_violations.extend(violations)
            
            # Generate comment for this file
            if violations:
                comment = format_review_comment(violations, file_path)
                review_comments.append(comment)
                
                # Check if there are any errors
                if any(v.severity == 'error' for v in violations):
                    has_errors = True
                    
        except Exception as e:
            print(f"Error reviewing {file_path}: {e}")
            error_comment = f"## ❌ Error reviewing `{file_path}`\n\nFailed to analyze file: {str(e)}"
            review_comments.append(error_comment)
            has_errors = True
    
    # Generate final review comment
    if review_comments:
        final_comment = f"# 🤖 Automated Code Review - PR #{args.pr_number}\n\n"
        final_comment += f"Reviewed {len(changed_files)} Python files.\n\n"
        final_comment += "---\n\n".join(review_comments)
        final_comment += "\n\n---\n\n"
        final_comment += "💡 **Tips:**\n"
        final_comment += "- ❌ **Errors** should be fixed before merging\n"
        final_comment += "- ⚠️ **Warnings** are strongly recommended to fix\n"
        final_comment += "- ℹ️ **Suggestions** are nice-to-have improvements\n\n"
        final_comment += "*This review was generated automatically. Please address the feedback and feel free to ask questions!*"
    else:
        final_comment = f"# ✅ Automated Code Review - PR #{args.pr_number}\n\n"
        final_comment += f"Great job! All {len(changed_files)} Python files passed the automated review checks.\n\n"
        final_comment += "No issues found with:\n"
        final_comment += "- Hardcoded secrets\n"
        final_comment += "- Error handling\n"
        final_comment += "- Function length\n"
        final_comment += "- Documentation\n"
        final_comment += "- Naming conventions\n\n"
        final_comment += "*This review was generated automatically.*"
    
    # Write outputs for GitHub Action
    with open('review_comment.md', 'w', encoding='utf-8') as f:
        f.write(final_comment)
    
    # Write status for GitHub Action
    status = 'errors' if has_errors else 'success'
    with open('review_status.txt', 'w') as f:
        f.write(status)
    
    # Set GitHub Action output
    print(f"::set-output name=has_violations::{len(all_violations) > 0}")
    print(f"::set-output name=has_errors::{has_errors}")
    print(f"::set-output name=violation_count::{len(all_violations)}")
    
    # Print summary
    print(f"\nReview Summary:")
    print(f"- Files reviewed: {len(changed_files)}")
    print(f"- Total violations: {len(all_violations)}")
    print(f"- Errors: {len([v for v in all_violations if v.severity == 'error'])}")
    print(f"- Warnings: {len([v for v in all_violations if v.severity == 'warning'])}")
    print(f"- Suggestions: {len([v for v in all_violations if v.severity == 'info'])}")
    
    if has_errors:
        print("\n❌ Review failed due to errors. Please fix before merging.")
        sys.exit(1)
    else:
        print("\n✅ Review completed successfully!")


if __name__ == "__main__":
    main()
