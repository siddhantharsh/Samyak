.PHONY: install test demo lint sweep data guard diagnose

diagnose:
	python3 -m scripts.evaluate_l1_coverage

guard:
	python3 -m scripts.run_guard

data:
	python3 -m sim.generate
install:
	pip install -e .

test:
	pytest || test $$? -eq 5

demo:
	python3 -m sim.compare

lint:
	ruff check .

sweep:
	@echo "Running sweep..."

restraint:
	python3 -m scripts.evaluate_ev
