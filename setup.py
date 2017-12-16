import os
import distutils.ccompiler as cc
import logging
import tempfile
import hashlib
import tarfile

from setuptools.command.build_ext import build_ext
from setuptools import Extension
from setuptools import setup

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen


DWM_VERSION = '6.1'
DWM_SRC_ROOT_DIR = 'dwm_src'
DWM_SRC_DIR = os.path.join(DWM_SRC_ROOT_DIR, 'dwm-{version}').format(
    version=DWM_VERSION
)
DWM_SOURCE = (
    'https://dl.suckless.org/dwm/dwm-{version}.tar.gz'.format(
        version=DWM_VERSION
    )
)
DWM_MD5 = 'f0b6b1093b7207f89c2a90b848c008ec'


dwm = Extension(
    'dwm',
    libraries=['X11', 'Xinerama', 'fontconfig', 'Xft'],
    library_dirs=['/usr/X11R6/lib'],
    include_dirs=[
        '/usr/X11R6/include',
        '/usr/include/freetype2',
        DWM_SRC_DIR,
    ],
    define_macros=[
            ('_DEFAULT_SOURCE',),
            ('_BSD_SOURCE',),
            ('_POSIX_C_SOURCE', 2),
            ('VERSION', '"{version}"'.format(version=DWM_VERSION)),
            ('XINERAMA',),
    ],
    sources=[
        os.path.join(DWM_SRC_DIR, 'drw.c'),
        os.path.join(DWM_SRC_DIR, 'dwm.c'),
        os.path.join(DWM_SRC_DIR, 'util.c'),
    ],
    extra_compile_args=[
        '-c',
        '-fPIC',
        '-std=c99',
        '-pedantic',
        '-Wno-deprecated-declarations',
        '-Os',
    ],
    extra_link_args=[
        '-fPIC',
    ]
)


class BuildDwm(build_ext, object):
    def relative_path(self, *dirs):
        return os.path.join(os.path.dirname(__file__), *dirs)

    def download_dwm(self):
        if not os.path.exists(self.relative_path(DWM_SRC_DIR)):
            logger = logging.getLogger()
            logger.warn('Downloading {file}...'.format(file=DWM_SRC_DIR))
            response = urlopen(DWM_SOURCE)
            data = response.read()

            os.mkdir(self.relative_path(DWM_SRC_ROOT_DIR))

            logger.warn('Validating MD5...')
            assert(hashlib.md5(data).hexdigest() == DWM_MD5)

            logger.warn('Extracting...')
            with tempfile.TemporaryFile() as destination_file:
                destination_file.write(data)
                destination_file.seek(0)
                with tarfile.open(
                    fileobj=destination_file,
                    mode='r:gz'
                ) as archive:
                    archive.extractall(DWM_SRC_ROOT_DIR)
                    destination_file.close()

    def copy_default_config(self):
        dest_file_path = self.relative_path(DWM_SRC_DIR, 'config.h')
        if not os.path.exists(dest_file_path):
            source_file = open(
                self.relative_path(
                    DWM_SRC_DIR, 'config.def.h'
                ),
                'r'
            )
            dest_file = open(dest_file_path, 'w')
            dest_file.write(source_file.read())
            source_file.close()
            dest_file.close()

    def build_extension(self, ext):
        self.download_dwm()
        self.copy_default_config()
        self.compiler = cc.new_compiler()
        return super(BuildDwm, self).build_extension(ext)

    def get_export_symbols(self, ext):
        return ext.export_symbols

    def get_ext_filename(self, ext_name):
        return ext_name + '.so'

setup(
    name='pydwm',
    url='https://github.com/benwah/pydwm',
    author='Benoit C. Sirois',
    author_email='benoitcsirois@gmail.com',
    version='0.1.3',
    description='A simple python wrapper around DWM.',
    long_description=(
        'This is a very simple python wrapper around DWM. It downloads DWM, '
        'compiles it as a shared object and exposes DWM\'s main function as '
        'pydwm:init_dwm. Installing this via pip will give you a pydwm '
        'executable, which just runs dwm.'
    ),
    packages=['pydwm'],
    include_package_data=True,
    license='MIT License',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Desktop Environment :: Window Managers',
    ],
    cmdclass={'build_ext': BuildDwm},
    ext_modules=[dwm],
    entry_points={
        'console_scripts': [
            'pydwm = pydwm:init_dwm',
        ]
    }
)
