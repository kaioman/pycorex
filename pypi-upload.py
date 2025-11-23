import filecmp
import sys
import os
import shutil
import subprocess
import LibHanger.Library.uwMessage as msg

# パッケージ名
package_name = 'pycorex'

# TestPyPIアップロード確認
ret = msg.confirmMessageDialog('Did you upload the package to TestPyPI?', 'Verification')
if ret == False:
    sys.exit()

# .pypircをユーザーフォルダ直下にコピー
src_pypirc = '.pypirc'
des_pypirc = os.path.expanduser('~/.pypirc')
shutil.copyfile(src_pypirc, des_pypirc)

# .pypircの内容が同一かチェック
if filecmp.cmp(src_pypirc,des_pypirc) == False:
    print('.pypirc is invalid')
    sys.exit()

# PyPIアップロード
subprocess.run(['twine','upload','-r','pypi','dist/*'],shell=True)

# PyPI-pipインストール
subprocess.run(['pip','install',package_name],shell=True)

# アンインストール
subprocess.run(['pip','uninstall','-y',package_name],shell=True)
