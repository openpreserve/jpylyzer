# -*- mode: python -*-

a = Analysis(['cli.py'],
            pathex=['jpylyzer'],
            hiddenimports=[],
            datas = [],
            hookspath=None)

pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name='jpylyzer.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True,
          contents_directory=".")

coll = COLLECT(exe,
               a.binaries +
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='jpylyzer')
