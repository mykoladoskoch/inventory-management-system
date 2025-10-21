# Contributing to Small Business Inventory Management System

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a new branch for your feature or bugfix
4. Make your changes
5. Test your changes thoroughly
6. Submit a pull request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/small-business-system.git
cd small-business-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python data/init_db.py

# Run the application
python app.py
```

## Code Style Guidelines

- Follow PEP 8 style guide for Python code
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and concise
- Comment complex logic

## Security Guidelines

- Never commit sensitive data (API keys, passwords, etc.)
- Always use parameterized queries for database operations
- Validate and sanitize all user inputs
- Use `json.loads()` instead of `eval()` for parsing JSON
- Keep dependencies up to date

## Testing

Before submitting a pull request:

1. Test all modified functionality manually
2. Ensure no existing features are broken
3. Test with sample data files
4. Verify database operations work correctly
5. Check for any console errors

## Pull Request Process

1. Update the README.md if you add new features
2. Update requirements.txt if you add new dependencies
3. Ensure your code follows the style guidelines
4. Write a clear description of your changes
5. Reference any related issues

## Types of Contributions

### Bug Fixes
- Clearly describe the bug and how to reproduce it
- Explain your fix and why it works
- Test thoroughly before submitting

### New Features
- Discuss major features in an issue first
- Keep features focused and well-documented
- Update documentation as needed
- Add sample data if applicable

### Documentation
- Fix typos and improve clarity
- Add examples and use cases
- Update outdated information
- Improve installation instructions

### Performance Improvements
- Benchmark before and after changes
- Explain the optimization approach
- Ensure no functionality is broken

## Code Review Process

All submissions require review. We use GitHub pull requests for this purpose. Reviewers will check for:

- Code quality and style
- Security considerations
- Performance implications
- Documentation completeness
- Test coverage

## Questions?

Feel free to open an issue for:
- Questions about the codebase
- Feature requests
- Bug reports
- General discussions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
