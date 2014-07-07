AUTH_CACHE_STORAGE=/tmp/tokens

tests: install_dummy_tokens bin/basic_agent src/config.py
	@py.test --junitxml results.xml src/*tests.py

install_dummy_tokens:
	install --directory         ${AUTH_CACHE_STORAGE}
	install magic_tokens/*.json ${AUTH_CACHE_STORAGE}

bin/basic_agent: support_tools/src/basic_agent.c
	make -C support_tools deps_install
	(cd support_tools && make basic_agent)
	mkdir -p bin
	mv support_tools/basic_agent bin/

src/config.py: src/config.py.dist
	cp -np src/config.py.dist src/config.py

clean:
	rm -f  src/config.py

distclean: clean
	make -C support_tools distclean
	rm -fr bin

