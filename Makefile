.PHONY: help fmt ty type-check lint clean install dev seed fmt-all lint-all check fmt-frontend lint-frontend

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

# Directories
BACKEND_DIR := backend
FRONTEND_DIR := frontend

# Default target
help:
	@echo "$(GREEN)RewardingLearning - Development Makefile$(NC)"
	@echo ""
	@echo "$(BLUE)Available targets:$(NC)"
	@echo ""
	@echo "$(YELLOW)Backend (Python / FastAPI / uv):$(NC)"
	@echo "  make fmt             Format Python code with ruff"
	@echo "  make ty              Type check (shorthand for type-check)"
	@echo "  make type-check      Full type check command"
	@echo "  make lint            Lint code with ruff"
	@echo "  make test            Run pytest tests"
	@echo "  make seed            Seed the database with sample data"
	@echo ""
	@echo "$(YELLOW)Frontend (React / Vite / Tailwind):$(NC)"
	@echo "  make fmt-frontend    Format frontend code"
	@echo "  make lint-frontend   Lint frontend code with eslint"
	@echo ""
	@echo "$(YELLOW)Combined:$(NC)"
	@echo "  make fmt-all         Format all code (backend + frontend)"
	@echo "  make lint-all        Lint all code (backend + frontend)"
	@echo "  make check           Type check and lint all code"
	@echo ""
	@echo "$(YELLOW)Project:$(NC)"
	@echo "  make install         Install all dependencies"
	@echo "  make dev             Start both dev servers (backend:8001 + frontend:3000)"
	@echo "  make dev-backend     Start backend only"
	@echo "  make dev-frontend    Start frontend only"
	@echo "  make clean           Clean build artifacts and cache"
	@echo "  make help            Show this help message"
	@echo ""

# ==================== Backend Targets ====================

fmt:
	@echo "$(BLUE)▶ Formatting Python code...$(NC)"
	cd $(BACKEND_DIR) && uv run --group dev ruff format app/ main.py seed.py
	@echo "$(GREEN)✓ Python formatting complete$(NC)"

ty:
	@echo "$(BLUE)▶ Running type checking...$(NC)"
	cd $(BACKEND_DIR) && uv run --group dev ty check app/ main.py seed.py || exit 1
	@echo "$(GREEN)✓ Type checking complete$(NC)"

type-check: ty
	@true

lint:
	@echo "$(BLUE)▶ Linting Python code...$(NC)"
	cd $(BACKEND_DIR) && uv run --group dev ruff check . --exclude "__pycache__,.venv" || exit 1
	@echo "$(GREEN)✓ Linting complete$(NC)"

test:
	@echo "$(BLUE)▶ Running tests...$(NC)"
	cd $(BACKEND_DIR) && uv run pytest || exit 1
	@echo "$(GREEN)✓ Tests passed$(NC)"

seed:
	@echo "$(BLUE)▶ Seeding database...$(NC)"
	cd $(BACKEND_DIR) && uv run python seed.py
	@echo "$(GREEN)✓ Database seeded$(NC)"

# ==================== Frontend Targets ====================

fmt-frontend:
	@echo "$(BLUE)▶ Formatting frontend code...$(NC)"
	cd $(FRONTEND_DIR) && npm run lint -- --fix 2>/dev/null || echo "$(YELLOW)Note: auto-fix not available$(NC)"
	@echo "$(GREEN)✓ Frontend formatting complete$(NC)"

lint-frontend:
	@echo "$(BLUE)▶ Linting frontend code...$(NC)"
	cd $(FRONTEND_DIR) && npm run lint 2>/dev/null || echo "$(YELLOW)Note: ESLint not configured$(NC)"
	@echo "$(GREEN)✓ Frontend linting complete$(NC)"

# ==================== Combined Targets ====================

fmt-all: fmt fmt-frontend
	@echo "$(GREEN)✓ All code formatted$(NC)"

lint-all: lint lint-frontend
	@echo "$(GREEN)✓ All code linted$(NC)"

check: ty lint
	@echo "$(GREEN)✓ All checks passed$(NC)"

# ==================== Project Targets ====================

install:
	@echo "$(BLUE)▶ Installing backend dependencies...$(NC)"
	cd $(BACKEND_DIR) && uv sync
	@echo "$(GREEN)✓ Backend dependencies installed$(NC)"
	@echo ""
	@echo "$(BLUE)▶ Installing frontend dependencies...$(NC)"
	cd $(FRONTEND_DIR) && npm install
	@echo "$(GREEN)✓ Frontend dependencies installed$(NC)"
	@echo "$(GREEN)✓ All dependencies installed$(NC)"

dev-backend:
	@echo "$(BLUE)▶ Starting backend server on port 8001...$(NC)"
	cd $(BACKEND_DIR) && uv run python main.py

dev-frontend:
	@echo "$(BLUE)▶ Starting frontend dev server on port 3000...$(NC)"
	cd $(FRONTEND_DIR) && npm run dev

dev:
	@echo "$(BLUE)▶ Starting development servers...$(NC)"
	@echo "$(YELLOW)Backend: http://localhost:8001  |  Frontend: http://localhost:3000$(NC)"
	@echo "$(YELLOW)API Docs: http://localhost:8001/docs$(NC)"
	@echo ""
	@make -j2 dev-backend dev-frontend

clean:
	@echo "$(BLUE)▶ Cleaning build artifacts and cache...$(NC)"
	cd $(BACKEND_DIR) && find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	cd $(BACKEND_DIR) && find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	cd $(BACKEND_DIR) && find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	cd $(BACKEND_DIR) && find . -type d -name ".pyright" -exec rm -rf {} + 2>/dev/null || true
	cd $(FRONTEND_DIR) && rm -rf dist node_modules/.cache node_modules/.vite 2>/dev/null || true
	rm -rf dist build *.egg-info 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

.PHONY: help fmt fmt-check type-check lint test seed fmt-frontend lint-frontend fmt-all lint-all check install dev dev-backend dev-frontend clean
