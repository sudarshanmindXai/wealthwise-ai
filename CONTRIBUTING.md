# Contributing to WealthWise AI

Thank you for considering contributing to WealthWise AI! This document provides guidelines and instructions for contributing.

---

## 🤝 Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:

- ✅ Be respectful and professional
- ✅ Focus on constructive feedback
- ✅ Help newcomers feel welcome
- ❌ No harassment, discrimination, or inappropriate behavior

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- Git installed
- OpenRouter API key (for testing document extraction)
- Basic understanding of FastAPI and Streamlit

### Development Setup

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/wealthwise-ai.git
   cd wealthwise-ai
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run tests to verify setup**
   ```bash
   pytest
   ```

---

## 📝 How to Contribute

### Reporting Bugs

Before creating a bug report:
- Check existing issues to avoid duplicates
- Collect relevant information (error messages, logs, screenshots)

**Bug Report Template:**
```markdown
**Description**: Brief summary of the bug

**Steps to Reproduce**:
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**: What should happen

**Actual Behavior**: What actually happens

**Environment**:
- OS: Windows 11 / macOS 14 / Ubuntu 22.04
- Python Version: 3.11.5
- WealthWise Version: 2.0.0

**Additional Context**: Screenshots, logs, etc.
```

### Suggesting Features

Feature suggestions are welcome! Please:
- Check if the feature already exists or is planned
- Explain the use case and benefit
- Provide examples or mockups if possible

**Feature Request Template:**
```markdown
**Problem Statement**: What problem does this solve?

**Proposed Solution**: How should it work?

**Alternatives Considered**: Other approaches you've thought about

**Additional Context**: Mockups, examples, references
```

---

## 🔧 Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

**Branch Naming Conventions:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions or fixes

### 2. Make Your Changes

**Code Style:**
- Follow PEP 8 for Python code
- Use type hints where possible
- Add docstrings to functions and classes
- Keep functions focused and small

**Example:**
```python
def calculate_tax(income: float, regime: str) -> float:
    """
    Calculate tax liability for given income and regime.
    
    Args:
        income: Gross taxable income in INR
        regime: Tax regime ('old' or 'new')
    
    Returns:
        Total tax liability in INR
    
    Raises:
        ValueError: If regime is invalid
    """
    if regime not in ['old', 'new']:
        raise ValueError(f"Invalid regime: {regime}")
    
    # Implementation...
    return tax_amount
```

### 3. Write Tests

All new features and bug fixes should include tests:

```python
# test_your_feature.py
import pytest
from src.your_module import your_function

def test_your_function_positive_case():
    """Test normal operation"""
    result = your_function(input_value)
    assert result == expected_value

def test_your_function_edge_case():
    """Test edge cases"""
    with pytest.raises(ValueError):
        your_function(invalid_input)
```

Run tests:
```bash
pytest -v
pytest --cov=src --cov-report=html
```

### 4. Update Documentation

- Update relevant README sections
- Add docstrings to new functions
- Update API documentation if endpoints changed
- Add examples if introducing new features

### 5. Commit Your Changes

**Commit Message Format:**
```
<type>: <short summary>

<optional detailed description>

<optional footer>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Formatting (no code change)
- `refactor:` - Code restructuring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

**Examples:**
```bash
git commit -m "feat: add support for ITR-5 form selection"
git commit -m "fix: resolve document extraction timeout issue"
git commit -m "docs: update installation instructions for Windows"
```

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

**PR Template:**
```markdown
**Description**: Brief overview of changes

**Related Issue**: Closes #123

**Type of Change**:
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

**Testing**:
- [ ] All tests pass
- [ ] Added new tests for this change
- [ ] Manually tested the feature

**Checklist**:
- [ ] Code follows PEP 8 style guidelines
- [ ] Added docstrings and type hints
- [ ] Updated documentation
- [ ] No breaking changes (or documented if unavoidable)
```

---

## 🧪 Testing Guidelines

### Test Categories

1. **Unit Tests** (`src/tests/`)
   - Test individual functions
   - Mock external dependencies
   - Fast execution

2. **Integration Tests** (`test_scenarios.py`)
   - Test API endpoints
   - Test full workflows
   - Use test fixtures

3. **Smoke Tests** (`test_scenarios_smoke.py`)
   - Quick validation
   - Critical paths only

### Running Tests

```bash
# All tests
pytest

# Specific file
pytest src/tests/test_contracts.py

# With coverage
pytest --cov=src --cov-report=html

# Verbose mode
pytest -v -s
```

---

## 📋 Code Review Process

### What We Look For

✅ **Code Quality**
- Follows PEP 8 style
- Type hints used
- No code duplication
- Proper error handling

✅ **Testing**
- Tests included
- Edge cases covered
- No failing tests

✅ **Documentation**
- Docstrings added
- README updated
- Examples provided

✅ **Compatibility**
- No breaking changes (unless necessary)
- Backward compatible APIs
- Python 3.11+ compatible

### Review Timeline

- Initial review within 2-3 business days
- Feedback addressed promptly
- Merge after approval from maintainers

---

## 🎯 Areas for Contribution

### High Priority

- 🔴 **Bug Fixes**: Always welcome
- 🟠 **Test Coverage**: Increase test coverage
- 🟡 **Documentation**: Improve clarity and examples

### Feature Areas

- **Document Extraction**: Add support for new document types
- **Tax Engine**: Enhance calculation accuracy
- **UI/UX**: Improve user experience
- **Scenarios**: Add more tax-saving scenarios
- **Validation**: Strengthen input validation

### Good First Issues

Look for issues labeled `good-first-issue` on GitHub.

---

## 💡 Development Tips

### Running in Development Mode

**Backend (with auto-reload):**
```bash
cd src/api
uvicorn app:app --reload --log-level debug
```

**Frontend (with auto-refresh):**
```bash
streamlit run streamlit_app.py --server.runOnSave true
```

### Debugging

**Enable debug logging:**
```python
# In your code
import logging
logging.basicConfig(level=logging.DEBUG)
```

**VS Code launch.json:**
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["src.api.app:app", "--reload"],
      "jinja": true
    }
  ]
}
```

### Common Issues

**Import errors:**
- Ensure you're in the project root
- Activate virtual environment
- Install all dependencies

**Test failures:**
- Clear `__pycache__` folders
- Update dependencies: `pip install -r requirements.txt --upgrade`
- Check if API key is set (for integration tests)

---

## 📞 Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Create a GitHub Issue
- **Chat**: Join our community (if available)

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to WealthWise AI! 🙏**
