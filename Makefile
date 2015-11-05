.PHONY: tags all

all:
	false

tags: .tags

.tags: *.py */*.py */*/*.py */*/*/*.py */*/*/*/*.py
	ctags -f $@ --python-kinds=-i -R

%.py:
	@true # For Python files not found by `tags`
