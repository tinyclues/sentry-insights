develop:
	pip install -e .
	pip install "file://`pwd`#egg=sentry-insights[test]"

test: develop
	py.test
