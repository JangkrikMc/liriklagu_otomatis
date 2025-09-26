# Contributing to Automatic Lyrics Generator

Thank you for your interest in contributing to the Automatic Lyrics Generator project! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project.

## How to Contribute

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes
4. Run tests to ensure your changes don't break existing functionality
5. Submit a pull request

## Development Setup

1. Clone your forked repository
2. Run the installation script:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```
3. Activate the virtual environment:
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

## Testing

Before submitting a pull request, please run the test script to ensure everything works correctly:

```bash
python src/test.py
```

## Pull Request Process

1. Update the README.md with details of changes if applicable
2. Update the documentation if you've changed functionality
3. The PR should work on Python 3.8 and above
4. Your PR will be reviewed by maintainers, who may request changes

## Style Guidelines

- Follow PEP 8 style guidelines for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Write docstrings for functions and classes

## License

By contributing to this project, you agree that your contributions will be licensed under the project's MIT License.