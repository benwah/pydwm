import os
import distutils.ccompiler as cc
import logging
import tempfile
import hashlib
import tarfile
import shutil

from setuptools.command.build_ext import build_ext
from setuptools.command.install import install
from setuptools import (Extension, setup)

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen


DWM_VERSION = '6.2'
DWM_SRC_ROOT_DIR= os.path.join('dwm_src')
DWM_REMOTE_SOURCE = (
    'https://dl.suckless.org/dwm/dwm-{version}.tar.gz'.format(
        version=DWM_VERSION
    )
)
DWM_MD5 = '9929845ccdec4d2cc191f16210dd7f3d'


class DwmExtension(Extension):
    def __init__(self, *args, **kwargs):
        super(DwmExtension, self).__init__(*args, **kwargs)

    def set_dwm_options(self, dwm_version):
        self.define_macros=[
            ('_DEFAULT_SOURCE',),
            ('_BSD_SOURCE',),
            ('_POSIX_C_SOURCE', 2),
            ('VERSION', '"{version}"'.format(version=dwm_version)),
            ('XINERAMA',),
        ]


def relative_path(*parts):
    return os.path.join(os.path.dirname(__file__), *parts)


dwm = DwmExtension(
    'dwm',
    libraries=['X11', 'Xinerama', 'fontconfig', 'Xft'],
    library_dirs=['/usr/X11R6/lib'],
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
    ],
    include_dirs=[
        '/usr/X11R6/include',
        '/usr/include/freetype2',
        relative_path(DWM_SRC_ROOT_DIR),
    ],
    sources=[
        relative_path(DWM_SRC_ROOT_DIR, 'drw.c'),
        relative_path(DWM_SRC_ROOT_DIR, 'dwm.c'),
        relative_path(DWM_SRC_ROOT_DIR, 'util.c'),
    ],
)


class BuildDwm(build_ext, object):
    user_options = build_ext.user_options + [
        ('dwm-source=', None, 'Path to DWM source')
    ]

    def initialize_options(self):
        self.dwm_source = None
        super(BuildDwm, self).initialize_options()

    def download_dwm(self):
        if not os.path.exists(relative_path(DWM_SRC_ROOT_DIR)):
            logger = logging.getLogger()
            logger.warn('Downloading {file}...'.format(file=DWM_SRC_ROOT_DIR))
            response = urlopen(DWM_REMOTE_SOURCE)
            data = response.read()

            os.mkdir(relative_path(DWM_SRC_ROOT_DIR))

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
                    unpacked_dest = 'dwm-{version}'.format(version=DWM_VERSION)
                    unpacked_dest = relative_path(
                        DWM_SRC_ROOT_DIR,
                        unpacked_dest
                    )
                    for file in os.listdir(unpacked_dest):
                        shutil.move(
                            relative_path(unpacked_dest, file),
                            relative_path(DWM_SRC_ROOT_DIR),
                        )

    def copy_default_config(self):
        dest_file_path = relative_path(DWM_SRC_ROOT_DIR, 'config.h')
        if not os.path.exists(dest_file_path):
            source_file = open(
                relative_path(
                    DWM_SRC_ROOT_DIR, 'config.def.h'
                ),
                'r'
            )
            dest_file = open(dest_file_path, 'w')
            dest_file.write(source_file.read())
            source_file.close()
            dest_file.close()

    def copy_dwm_source(self):
        if not os.path.exists(relative_path(DWM_SRC_ROOT_DIR)):
            shutil.copytree(self.dwm_source, DWM_SRC_ROOT_DIR)

    def build_extension(self, ext):
        if ext.name == 'dwm':
            self.compiler = cc.new_compiler()

            if self.dwm_source is None:
                self.download_dwm()
                self.copy_default_config()
            else:
                self.copy_dwm_source()

        del(self.dwm_source)
        return super(BuildDwm, self).build_extension(ext)

    def get_export_symbols(self, ext):
        return ext.export_symbols

    def get_ext_filename(self, ext_name):
        return ext_name + '.so'

    @property
    def dwm_version(self):
        return 'custom' if self.dwm_source else VERSION

setup(
    name='pydwm',
    url='https://github.com/benwah/pydwm',
    author='Benoit C. Sirois',
    author_email='benoitcsirois@gmail.com',
    version='0.1.4',
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
