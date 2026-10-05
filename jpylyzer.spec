# -*- mode: python -*-
a = Analysis(['.\cli.py'],
            pathex=['.\jpylyzer'],
            hiddenimports=[],
            datas = [
                    ('./license/LICENSE.txt', 'license'),
                    (''./doc/jpylyzerUserManual.html', 'doc'),
                    ('./example_files/*', 'example_files')]
            hookspath=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
            a.scripts,
            exclude_binaries=True,
            name='jpylyzer.exe',
            debug=False,
            strip=False,
            upx=True,
            console=True)
