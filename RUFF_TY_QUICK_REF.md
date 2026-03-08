# 🚀 Quick Reference - Updated Makefile

## New Commands

### Format Code (Ruff)
```bash
make fmt    # Format Python code with ruff
```

### Type Check (Pyright) - Shorthand
```bash
make ty     # Type check (SHORT - new!)
```

### Type Check - Full Name
```bash
make type-check    # Type check (FULL NAME - alias)
```

### Lint Code (Ruff)
```bash
make lint   # Lint Python code with ruff
```

### Run All Checks
```bash
make check  # Type-check + lint combined
```

---

## Most Used Commands

| Command | Does | Speed |
|---------|------|-------|
| `make fmt` | Format code with Ruff | ⚡ Fast |
| `make ty` | Type check with Pyright | ⚡ Fast |
| `make lint` | Lint with Ruff | ⚡ Fast |
| `make check` | All checks (ty + lint) | ⚡ Fast |

---

## Typical Workflow

```bash
# 1. Format your code
make fmt

# 2. Quick type check
make ty

# 3. Check for issues
make lint

# OR do all at once
make check
```

---

## Why Ruff?

- ✅ **Fast** - Written in Rust
- ✅ **Simple** - One tool for format + lint
- ✅ **Modern** - Latest Python tooling
- ✅ **Compatible** - Works with Pyright

---

## Tools Used

| Tool | Purpose | Command |
|------|---------|---------|
| **Ruff** | Format + Lint | `make fmt` / `make lint` |
| **Pyright** | Type Check | `make ty` |
| **Pytest** | Testing | `make test` |

---

**Status**: ✅ Ready to use!

See `MAKEFILE_RUFF_TY_UPDATE.md` for detailed information.

