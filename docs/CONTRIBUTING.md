# Contributing to IQDB API Python

Cảm ơn bạn đã quan tâm đến việc đóng góp cho IQDB API Python! 

## 🚀 Getting Started

### Prerequisites
- Python 3.8 hoặc cao hơn
- Git
- Basic knowledge về async/await Python

### Development Setup

1. **Fork repository**
   ```bash
   # Fork trên GitHub, sau đó clone
   git clone https://github.com/hieuxyz00/iqdb-api-python.git
   cd iqdb-api-python
   ```

2. **Setup development environment**
   ```bash
   # Tạo virtual environment
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate   # Windows
   
   # Install development dependencies
   pip install -e ".[dev]"
   ```

3. **Verify setup**
   ```bash
   # Run syntax tests
   python test_syntax.py
   
   # Run unit tests (if available)
   pytest tests/ -v
   ```

## 📝 Development Guidelines

### Code Style

Chúng tôi sử dụng **Black** cho code formatting:

```bash
# Format code
black src/ tests/ examples/

# Check formatting
black --check src/ tests/ examples/
```

### Type Checking

Sử dụng **mypy** cho type checking:

```bash
# Check types
mypy src/

# Check specific file
mypy src/iqdb_api/client.py
```

### Linting

Sử dụng **flake8** cho linting:

```bash
# Lint code
flake8 src/ tests/

# Lint với specific config
flake8 --max-line-length=88 src/
```

### Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/iqdb_api --cov-report=html

# Run specific test
pytest tests/test_models.py -v
```

## 🔄 Contribution Workflow

### 1. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes
- Implement your feature
- Add tests nếu applicable
- Update documentation nếu needed
- Follow code style guidelines

### 3. Test Changes
```bash
# Run syntax tests
python test_syntax.py

# Run unit tests
pytest tests/ -v

# Check code style
black --check src/ tests/
flake8 src/ tests/
mypy src/
```

### 4. Commit Changes
```bash
git add .
git commit -m "feat: add your feature description"
```

**Commit Message Guidelines:**
- `feat:` - new feature
- `fix:` - bug fix  
- `docs:` - documentation changes
- `style:` - formatting, missing semi colons, etc
- `refactor:` - code change that neither fixes a bug nor adds a feature
- `test:` - adding missing tests
- `chore:` - updating grunt tasks etc; no production code change

### 5. Push và Create PR
```bash
git push origin feature/your-feature-name
```

Sau đó tạo Pull Request trên GitHub.

## 🐛 Bug Reports

Khi report bugs, vui lòng include:

- **Python version**: `python --version`
- **Library version**: Kiểm tra trong `src/iqdb_api/__init__.py`
- **Operating System**: Windows/Linux/macOS
- **Reproduction steps**: Detailed steps để reproduce bug
- **Expected behavior**: Behavior bạn expect
- **Actual behavior**: Behavior thực tế xảy ra
- **Error messages**: Full error messages nếu có
- **Code example**: Minimal code example để reproduce

### Bug Report Template
```markdown
**Environment:**
- Python version: 
- Library version:
- OS: 

**Description:**
Brief description of the bug

**Steps to Reproduce:**
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Error Message:**
```
Full error traceback
```

**Code Example:**
```python
# Minimal code to reproduce
```
```

## 💡 Feature Requests

Khi request features, vui lòng describe:

- **Use case**: Tại sao feature này hữu ích?
- **Proposed solution**: Làm thế nào bạn muốn nó work?
- **Alternatives**: Có alternative solutions nào không?
- **Examples**: Code examples nếu possible

## 📋 Development Tasks

### Common Tasks

**Add new exception:**
1. Add exception class trong `src/iqdb_api/exceptions.py`
2. Import trong `src/iqdb_api/__init__.py`
3. Add test case trong `tests/test_exceptions.py`
4. Update documentation

**Add new enum value:**
1. Add value trong appropriate enum trong `src/iqdb_api/enums.py`
2. Update parser nếu needed trong `src/iqdb_api/parser.py`
3. Add test case
4. Update documentation

**Improve parser:**
1. Modify `src/iqdb_api/parser.py`
2. Test với real IQDB responses
3. Ensure backward compatibility
4. Add test cases

### Testing Guidelines

- **Unit tests**: Test individual functions/methods
- **Integration tests**: Test client functionality (cẩn thận với rate limiting)
- **Mock tests**: Mock HTTP responses để test parser
- **Edge cases**: Test error conditions, empty responses, malformed data
- **Queue/Overload**: Test các trường hợp IQDB trả về queue/overload, kiểm tra trường queue_status và stream queue
- **Fallback download/upload**: Test khi gặp lỗi Not an image..., client sẽ tự động tải về và upload lại
- **Timeout**: Test timeout vô hạn và timeout custom

### Documentation Guidelines

- **Docstrings**: Google-style docstrings cho all public methods
- **Type hints**: Full type hints cho all parameters và returns
- **Examples**: Include examples trong docstrings, đặc biệt với queue/stream và fallback
- **README**: Update README.md nếu có public API changes, đặc biệt liên quan queue/fallback/timeout

## 🔧 Project Structure

```
iqdb_api_python/
├── src/iqdb_api/          # Main package
│   ├── __init__.py        # Package exports
│   ├── client.py          # Main clients
│   ├── models.py          # Data models
│   ├── enums.py           # Enumerations
│   ├── exceptions.py      # Custom exceptions
│   └── parser.py          # HTML parser
├── tests/                 # Unit tests
├── examples/              # Usage examples  
├── docs/                  # Documentation
├── requirements.txt       # Dependencies
├── pyproject.toml        # Modern packaging
├── setup.py              # Legacy packaging
└── README.md             # Main documentation
```

## 📊 Release Process

1. Update version trong `src/iqdb_api/__init__.py`
2. Update `CHANGELOG.md`
3. Create release tag: `git tag v1.0.1`
4. Push tags: `git push origin --tags`
5. Create GitHub release
6. Publish to PyPI (maintainers only)

## ❓ Questions?

- **GitHub Issues**: [Create an issue](https://github.com/hieuxyz00/iqdb-api-python/issues)
- **Discussions**: [GitHub Discussions](https://github.com/hieuxyz00/iqdb-api-python/discussions)

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🎉
