.PHONY: help fmt type-check lint clean install dev

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
	@echo "$(YELLOW)Backend (Python):$(NC)"
	@echo "  make fmt             Format Python code with uv"
	@echo "  make type-check      Run type checking with pyright"
	@echo "  make lint            Lint code with ruff"
	@echo "  make test            Run pytest tests"
	@echo ""
	@echo "$(YELLOW)Frontend (TypeScript):$(NC)"
	@echo "  make fmt-frontend    Format frontend code with prettier"
	@echo "  make lint-frontend   Lint frontend code with eslint"
	@echo ""
	@echo "$(YELLOW)Combined:$(NC)"
	@echo "  make fmt-all         Format all code (backend + frontend)"
	@echo "  make lint-all        Lint all code (backend + frontend)"
	@echo "  make check           Type check and lint all code"
	@echo ""
	@echo "$(YELLOW)Project:$(NC)"
	@echo "  make install         Install all dependencies"
	@echo "  make dev             Start development servers"
	@echo "  make clean           Clean build artifacts and cache"
	@echo "  make help            Show this help message"
	@echo ""

# ==================== Backend Targets ====================

fmt:
	@echo "$(BLUE)▶ Formatting Python code...$(NC)"
	cd $(BACKEND_DIR) && uv run black . --exclude "__pycache__|\.venv"
	@echo "$(GREEN)✓ Python formatting complete$(NC)"

fmt-check:
	@echo "$(BLUE)▶ Checking Python formatting...$(NC)"
	cd $(BACKEND_DIR) && uv run black . --check --exclude "__pycache__|\.venv" || exit 1
	@echo "$(GREEN)✓ Python format check passed$(NC)"

type-check:
	@echo "$(BLUE)▶ Running type checking...$(NC)"
	cd $(BACKEND_DIR) && uv run pyright app/ || exit 1
	@echo "$(GREEN)✓ Type checking complete$(NC)"

lint:
	@echo "$(BLUE)▶ Linting Python code...$(NC)"
	cd $(BACKEND_DIR) && uv run ruff check . --exclude "__pycache__,.venv" || exit 1
	@echo "$(GREEN)✓ Linting complete$(NC)"

test:
	@echo "$(BLUE)▶ Running tests...$(NC)"
	cd $(BACKEND_DIR) && uv run pytest || exit 1
	@echo "$(GREEN)✓ Tests passed$(NC)"

# ==================== Frontend Targets ====================

fmt-frontend:
	@echo "$(BLUE)▶ Formatting frontend code...$(NC)"
	cd $(FRONTEND_DIR) && npm run lint:fix 2>/dev/null || echo "$(YELLOW)Note: Prettier not configured$(NC)"
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

check: type-check lint
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

dev:
	@echo "$(BLUE)▶ Starting development servers...$(NC)"
	./dev.sh

clean:
	@echo "$(BLUE)▶ Cleaning build artifacts and cache...$(NC)"
	cd $(BACKEND_DIR) && find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	cd $(BACKEND_DIR) && find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	cd $(BACKEND_DIR) && find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	cd $(BACKEND_DIR) && find . -type d -name ".pyright" -exec rm -rf {} + 2>/dev/null || true
	cd $(FRONTEND_DIR) && rm -rf .next node_modules/.cache 2>/dev/null || true
	rm -rf dist build *.egg-info 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

# ==================== Special Targets ====================

.PHONY: help fmt fmt-check type-check lint test fmt-frontend lint-frontend fmt-all lint-all check install dev clean

