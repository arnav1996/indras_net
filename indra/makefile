TESTDIR = tests
PYLINT = flake8
PYLINTFLAGS = --ignore=E741,W503 --exclude=interactive.py,segregation.py
PYTHONFILES = $(shell ls *.py)
TEST_FILES = $(shell ls $(TESTDIR)/test_*.py)

prod: tests
	-git commit -a
	git push origin master

lint: $(patsubst %.py,%.pylint,$(PYTHONFILES))

pytests: $(PYTHONFILES)
	./pytests.sh

tests: pytests lint

%.pylint:
	$(PYLINT) $(PYLINTFLAGS) $*.py

nocrud:
	-rm *~
	-rm *.log
	-rm *.out
	-rm .*swp
	-rm *.csv
	-rm $(TESTDIR)/*~
