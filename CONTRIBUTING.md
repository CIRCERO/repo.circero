# Contributing to CIRCERO Repository

Thank you for your interest in contributing! This document provides guidelines for contributing to the CIRCERO Kodi addon repository.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the issue, not the person
- Help create a welcoming environment

## How to Contribute

### Reporting Issues

**Bug Reports**:
1. Check if issue already exists
2. Use the bug report template
3. Provide detailed information:
   - Kodi version
   - Addon version
   - Steps to reproduce
   - Expected vs actual behavior
   - Relevant logs
4. Be specific and concise

**Feature Requests**:
1. Check if feature already requested
2. Use the feature request template
3. Explain the use case
4. Describe the desired behavior
5. Consider implementation complexity

### Submitting Changes

#### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/repo.circero.git
cd repo.circero
```

#### 2. Create Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-description
```

Branch naming:
- `feature/` - New features
- `bugfix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring

#### 3. Make Changes

- Follow existing code style
- Add comments for complex logic
- Update documentation
- Test thoroughly

#### 4. Commit Changes

Use clear, descriptive commit messages:

```
Add support for NewSite scraper

- Implement scene search and details
- Add Kodi adapter
- Update settings and routing
- Add documentation and tests
```

Format:
- First line: Brief summary (50 chars or less)
- Blank line
- Detailed description with bullet points
- Reference issues: `Fixes #123` or `Closes #456`

#### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Create pull request on GitHub with:
- Clear title
- Detailed description
- Reference related issues
- Screenshots (if UI changes)
- Testing steps

### Pull Request Guidelines

**Before Submitting**:
- ✅ Code follows project style
- ✅ All tests pass
- ✅ Documentation updated
- ✅ Commits are clean and clear
- ✅ No unrelated changes
- ✅ Tested in Kodi

**PR Description Should Include**:
- What changed and why
- How to test the changes
- Any breaking changes
- Screenshots/logs (if applicable)

**After Submitting**:
- Respond to review feedback
- Make requested changes
- Keep PR updated with main branch

## Development Guidelines

### Code Style

**Python**:
- Follow PEP 8
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use descriptive variable names
- Add docstrings to functions

**Example**:
```python
def search_scenes(query, year=None):
    """
    Search for scenes by title and optional year
    
    Args:
        query (str): Search query string
        year (int, optional): Release year filter
        
    Returns:
        list: List of scene dictionaries
    """
    # Implementation
    pass
```

### Testing

**Manual Testing**:
1. Test in Kodi (version 19+)
2. Test all affected scrapers
3. Test error conditions
4. Check Kodi logs for errors

**Validation Scripts**:
```bash
python tools/validate_installation.py
python tools/validate_dependencies.py
```

### Documentation

**Update Documentation When**:
- Adding new scraper
- Changing configuration
- Adding new features
- Fixing bugs (if user-facing)

**Documentation Files**:
- `README.md` - Overview
- `docs/CONFIGURATION.md` - Configuration changes
- `docs/SCRAPERS.md` - New scrapers
- `docs/integrations/` - Scraper-specific docs
- `docs/CHANGELOG.md` - Version history

### Adding New Scrapers

See [Development Guide](docs/DEVELOPMENT.md) for detailed instructions.

**Checklist**:
- [ ] Implement scraper logic
- [ ] Create Kodi adapter
- [ ] Update `scraper.py`
- [ ] Update `settings.xml`
- [ ] Add translations
- [ ] Write documentation
- [ ] Add validation tests
- [ ] Test thoroughly
- [ ] Update CHANGELOG

## Project Structure

```
repo.circero/
├── metadata.stash.python/      # Main addon code
├── repository.circero/         # Repository addon
├── docs/                       # Documentation
├── tools/                      # Development tools
└── .github/                    # GitHub configuration
```

## Getting Help

- **Documentation**: Start with [docs/](docs/)
- **Discussions**: [GitHub Discussions](https://github.com/CIRCERO/repo.circero/discussions)
- **Issues**: Search existing issues first

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- GitHub contributors page
- Release notes (for significant contributions)
- CHANGELOG.md

## Questions?

If you have questions about contributing:
1. Check [Development Guide](docs/DEVELOPMENT.md)
2. Search existing issues and discussions
3. Ask in [GitHub Discussions](https://github.com/CIRCERO/repo.circero/discussions)

Thank you for contributing! 🎉
