build:
	pyinstaller jpylyzer.py
	@echo "Built in dist/jpylyzer/" 	

install:
#	pwd
	mv dist/jpylyzer/* $(DESTDIR)
	ln -s $(LINKDIR)/jpylyzer $(LINKDESTDIR)/jpylyzer
#	ln -s /tmp $(LINKDESTDIR)/jpylyzer

clean:
	rm -fR build
	rm -fR dist
	rm -f jpylyzer.spec
	rm -f logdict2.7.2.final.0-1.log
	rm -f logdict2.7.2.final.0-2.log
	rm -f logdict2.7.2.final.0-3.log
	rm -f warnjpylyzer.txt
