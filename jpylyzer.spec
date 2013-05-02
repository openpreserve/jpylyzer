# -*- mode: python -*-
a = Analysis(['.\\jpylyzer\\jpylyzer.py'],
             pathex=['F:\\johan\\pythonCode\\jpylyzer'],
             hiddenimports=[],
             hookspath=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=os.path.join('dist', 'jpylyzer.exe'),
          debug=False,
          strip=None,
          upx=True,
          console=True )
