
.PHONY: format

format:
	black 	scripts/gh_cli_adapter.py \
		scripts/repository_dependencies.py
