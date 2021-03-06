import cx_Freeze
import sys
import os

PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')
base = None

if sys.platform == 'win32':
    base = "Win32GUI"

executables = [cx_Freeze.Executable("Episode Tracker.py", base=base, icon= 'episode_tracker_icon.ico')]

with open('README.md', encoding="utf8") as f:
    readme = f.read()

with open('LICENSE.txt') as f:
    license = f.read()

cx_Freeze.setup(
    name= "Episode Tracker",
    author= "Mohit Bansal",
    author_email= "bansalmohit72@gmail.com",
    options= {'build_exe':{ 'packages': ['tkinter', 'os', 'sqlite3'],
                                        'include_files':['utils.py', 'tv_series_db.db',
                                        'episode_tracker_icon.ico',
                                        os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'),
                                        os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll')]}},
    version= "1.1",
    description= "Keep track of seen and unseen episodes of TV shows.",
    long_description= readme,
    license= license,
    executables= executables
    )