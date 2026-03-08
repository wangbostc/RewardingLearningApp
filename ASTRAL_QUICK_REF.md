# 🚀 Astral Toolchain - Quick Reference

## Your New Setup

You now have a complete **Astral** development toolchain:

```bash
make fmt        # Format with Ruff
make ty         # Type check with ty
make lint       # Lint with Ruff
make check      # Type check + lint
```

---

## All Tools from Astral

| Tool | Purpose | Status |
|------|---------|--------|
| **Ruff** | Format + Lint | ✅ |
| **ty** | Type Checker | ✅ |
| **Pytest** | Testing | ✅ |

---

## Commands Cheat Sheet

```bash
# Development workflow
make fmt        # Quick format
make ty         # Quick type check
make lint       # Quick lint
make check      # Full check suite

# Combined
make fmt && make ty && make lint

# Or just use
make check      # Does ty + lint
```

---

## Why Astral?

- ⚡ Fast (Rust-based)
- 🎯 Consistent (same vendor)
- 📦 Minimal (fewer tools needed)
- 🔄 Integrated (works seamlessly)

---

## Next Steps

1. `make fmt` to format
2. `make ty` to type check
3. `make check` for full validation

---

**Status**: ✅ Ready to use!

See `ASTRAL_TY_COMPLETE.md` for details.

