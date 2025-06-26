.PHONY: install format lint typecheck compile check

install:
	pip install -r requirements.txt

format:
	black summarise-video

lint:
	ruff check summarise-video

typecheck:
	mypy summarise-video

compile:
	python3 -m py_compile summarise-video

check: format lint typecheck compile

