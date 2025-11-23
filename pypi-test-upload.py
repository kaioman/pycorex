import filecmp
import sys
import os
import shutil
import subprocess
import LibHanger.Library.uwMessage as msg

# パッケージ名
package_name = 'pycorex'

# バージョン番号変更確認
ret = msg.confirmMessageDialog('Did you change the version number?', 'Verification')
if ret == False:
    sys.exit()

# ローカルインストール
subprocess.run(['python','setup.py','install'],shell=True)

# パッケージ関連ディレクトリの中身をクリーンアップ
if os.path.exists('build') : shutil.rmtree('build')
if os.path.exists('dist') : shutil.rmtree('dist')
if os.path.exists('pycorex.egg-info') : shutil.rmtree('pycorex.egg-info')

# パッケージング
subprocess.run(['python','setup.py','sdist','bdist_wheel'],shell=True)

# アンインストール
subprocess.run(['pip','uninstall','-y',package_name],shell=True)

# .pypircをユーザーフォルダ直下にコピー
src_pypirc = '.pypirc'
des_pypirc = os.path.expanduser('~/.pypirc')
shutil.copyfile(src_pypirc, des_pypirc)

# .pypircの内容が同一かチェック
if filecmp.cmp(src_pypirc,des_pypirc) == False:
    print('.pypirc is invalid')
    sys.exit()
    
# TestPyPIアップロード
subprocess.run(['twine','upload','--repository','testpypi','dist/*'],shell=True)

# TestPyPI-pipインストール
subprocess.run(['pip','install','--index-url', 'https://test.pypi.org/simple/','--no-deps',package_name],shell=True)

# アンインストール
subprocess.run(['pip','uninstall','-y',package_name],shell=True)
