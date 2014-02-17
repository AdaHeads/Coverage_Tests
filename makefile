AUTH_CACHE_STORAGE=/dev/shm/auth/

tests: install_dummy_tokens bin/basic_agent
	@py.test --junitxml results.xml src/*tests.py

install_dummy_tokens:
	install --directory         ${AUTH_CACHE_STORAGE}
	install magic_tokens/*.json ${AUTH_CACHE_STORAGE}

bin/basic_agent:
	make -C support_tools deps_install
	(cd support_tools && make basic_agent)
	-mkdir bin
	mv support_tools/basic_agent bin/
