.PHONY: install test demo lint sweep

install:
	pip install -e .

test:
	pytest || test $$? -eq 5

demo:
	@echo "Running demo..."

lint:
	ruff check .

sweep:
	@echo "Running sweep..."
