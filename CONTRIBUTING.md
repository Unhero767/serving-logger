# Contributing to MLAOS Serving Logger

Thank you for your interest in contributing to the MLAOS Serving Logger project.

## Project Owner

**Kenneth Dallmier** — Sole Engineer & Owner  
Contact: kennydallmier@gmail.com

## Development Setup

```bash
git clone https://github.com/Unhero767/serving-logger.git
cd serving-logger
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running Tests

```bash
pytest tests/ -v --cov=src --cov-report=term-missing
coverage report --fail-under=85
```

## Security Checks (Run Before Every Commit)

```bash
# Check for secrets in history
git log --all --full-history -- "**/*.env"
git log --all --full-history -- "**/*.key"
git log --all --full-history -- "**/credentials*"

# Scan for hardcoded passwords
grep -r "password=" . --exclude-dir=.git
grep -r "api_key=" . --exclude-dir=.git
grep -r "secret=" . --exclude-dir=.git

# Verify .gitignore is working
git check-ignore -v .env
git check-ignore -v credentials.json
```

## Google ML Rules Compliance

All contributions must maintain compliance with:

| Rule | Requirement |
|------|-------------|
| Rule #5 | Export data to files/DB and verify pipeline statistics |
| Rule #10 | Be aware of silent failures — logger must never crash inference |
| Rule #11 | Give feature columns owners and documentation |
| Rule #22 | Clean up features you are no longer using |
| Rule #29 | Log features at serving time |
| Rule #32 | Re-use code between training and serving pipelines |
| Rule #37 | Measure training/serving skew |

## Code Style

- Follow PEP 8
- All functions must have docstrings
- All new features require tests with >85% coverage
- No hardcoded credentials or connection strings
- Use environment variables for all configuration

## Commit Message Format

```
<type>: <short description> (Rule #XX if applicable)

Examples:
feat: Add resonance_score feature logging (Rule #29)
fix: Silent failure on DB timeout (Rule #10)
test: Add coverage for SkewAuditor.run_audit (Rule #37)
docs: Update API reference for log_inference
```

## Pull Request Checklist

- [ ] Tests pass: `pytest tests/ -v`
- [ ] Coverage >= 85%: `coverage report --fail-under=85`
- [ ] No secrets in code: security scan passes
- [ ] Docstrings on all new functions
- [ ] Google ML Rule compliance maintained
- [ ] `.gitignore` updated if new file types added

---

*MLAOS Infrastructure — serving-logger v1.0*
