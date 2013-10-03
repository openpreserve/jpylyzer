build:
	./build-with-pyinstaller.sh

install:
	mv pyi-build/dist/jpylyzer $(DESTDIR)

clean:
	rm -fR pyi-build
