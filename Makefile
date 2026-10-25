.PHONY: run test check
run:
	python3 -m aveniq

test:
	python3 -m unittest discover -v

check: test
	python3 -m compileall -q aveniq
	@command -v node >/dev/null && node --check web/app.js || true
