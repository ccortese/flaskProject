# 🤖 Automated PR Review Agent

This repository includes an automated code review system that checks Python files against 5 key coding standards:

1. **🔐 No Hardcoded Secrets** - Detects API keys, passwords, and tokens
2. **⚠️ Proper Error Handling** - Ensures risky operations use try/except
3. **📏 Function Length** - Keeps functions under 50 lines
4. **📚 Documentation** - Requires docstrings for public functions
5. **🐍 Naming Conventions** - Enforces snake_case naming

## 🚀 Quick Start

### GitHub Action (Automatic)

The review agent automatically runs on every PR that changes Python files.

**Setup:**
1. The GitHub Action is already configured in `.github/workflows/pr-review.yml`
2. It will automatically comment on PRs with review feedback
3. No additional setup required!

**What happens:**
- ✅ Triggers on PR creation/updates
- 🔍 Reviews only changed Python files
- 💬 Posts detailed feedback as PR comments
- 🚦 Sets commit status (pass/fail)

### Local Usage

Run reviews locally before creating PRs:

```bash
# Review a specific file
python local_pr_reviewer.py --file app.py

# Review all Python files
python local_pr_reviewer.py --all

# Review uncommitted changes
python local_pr_reviewer.py --changed

# Review files in a specific PR
python local_pr_reviewer.py --pr 123

# Post review as comment to PR
python local_pr_reviewer.py --pr 123 --post-comment
```

## 📋 Review Checks Explained

### 1. Hardcoded Secrets Detection
**What it checks:**
- API keys, passwords, tokens in string literals
- Suspicious long strings that might be secrets

**❌ Bad:**
```python
api_key = "sk-1234567890abcdef"
password = "mypassword123"
```

**✅ Good:**
```python
api_key = os.getenv('API_KEY')
password = os.getenv('PASSWORD')
```

### 2. Error Handling
**What it checks:**
- Database operations without try/except
- File I/O without error handling
- API calls without exception handling

**❌ Bad:**
```python
def save_user(user):
    db.session.add(user)
    db.session.commit()  # Could fail!
```

**✅ Good:**
```python
def save_user(user):
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
```

### 3. Function Length
**What it checks:**
- Functions longer than 50 lines

**💡 Suggestion:**
Break long functions into smaller, focused functions.

### 4. Documentation
**What it checks:**
- Public functions missing docstrings
- Functions with 3+ lines of code

**❌ Bad:**
```python
def calculate_total(items):
    total = 0
    for item in items:
        total += item.price
    return total
```

**✅ Good:**
```python
def calculate_total(items):
    """Calculate the total price of all items.
    
    Args:
        items: List of items with price attribute
        
    Returns:
        float: Total price of all items
    """
    total = 0
    for item in items:
        total += item.price
    return total
```

### 5. Naming Conventions
**What it checks:**
- Functions and variables using camelCase instead of snake_case
- Inconsistent naming patterns

**❌ Bad:**
```python
def getUserData():
    userName = "john"
```

**✅ Good:**
```python
def get_user_data():
    user_name = "john"
```

## 🔧 Configuration

### Local Setup

**Requirements:**
- Python 3.7+
- `requests` library for GitHub API calls

**Install dependencies:**
```bash
pip install requests
```

**GitHub Token (for PR features):**
```bash
# Set environment variable
export GITHUB_TOKEN="your_github_token"

# Or configure in git
git config github.token "your_github_token"
```

### GitHub Action Setup

The action is pre-configured but you can customize:

**File:** `.github/workflows/pr-review.yml`

**Customization options:**
- Change Python version
- Modify trigger conditions
- Add additional dependencies
- Customize comment format

## 📊 Output Formats

### Console Output (Default)
Human-readable format with colors and formatting.

### Markdown Output
```bash
python local_pr_reviewer.py --all --output markdown
```
Perfect for copying into GitHub comments.

### JSON Output
```bash
python local_pr_reviewer.py --all --output json
```
Machine-readable format for integration with other tools.

## 🎯 Severity Levels

- **❌ Errors**: Must be fixed before merging
- **⚠️ Warnings**: Should be fixed (strongly recommended)
- **ℹ️ Suggestions**: Nice-to-have improvements

## 🔍 Example Review Output

```markdown
## 🔍 Code Review for `app.py`

### ❌ Errors (Must Fix)
- **Line 211**: Potential hardcoded API key detected
  💡 *Use environment variables or config files for sensitive data*

### ⚠️ Warnings (Should Fix)
- **Line 58**: Function 'new_user' performs risky operations without error handling
  💡 *Add try/except blocks around database operations*

### ℹ️ Suggestions (Nice to Have)
- **Line 49**: Function 'load_main_page' is missing a docstring
  💡 *Add a docstring describing what the function does*
```

## 🚀 Advanced Usage

### Custom Review Rules
Modify `pr_review_agent.py` to add your own checks or adjust existing ones.

### Integration with CI/CD
The GitHub Action can be extended to:
- Block merging on errors
- Generate reports
- Integrate with other tools

### Team Workflow
1. Developers run local reviews before pushing
2. GitHub Action provides automated feedback on PRs
3. Team reviews focus on logic and architecture
4. Automated checks handle style and basic issues

## 🤝 Contributing

To add new review checks:
1. Add method to `CodeReviewer` class
2. Call from `review_file` method
3. Update documentation
4. Test with sample code

## 📝 License

This review agent is part of your Flask project and follows the same license terms.
