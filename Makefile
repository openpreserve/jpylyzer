install:
	tar xzf jpylyzer.tar.gz -C $(DESTDIR) 2>/dev/null
	ln -s $(LINKDIR)/jpylyzer $(LINKDESTDIR)/jpylyzer
