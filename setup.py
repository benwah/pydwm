import os
import distutils.ccompiler as cc

from setuptools.command.build_ext import build_ext
from setuptools import (Extension, setup)


def relative_path(*parts):
    return os.path.join('.', *parts)


DWM_VERSION = '6.3'
DWM_SRC_ROOT_DIR = relative_path('dwm_src')

dwm = Extension(
    'dwm',
    define_macros=[
        ('_DEFAULT_SOURCE', True),
        ('_BSD_SOURCE', True),
        ('_POSIX_C_SOURCE', 2),
        ('VERSION', '"{version}"'.format(version=DWM_VERSION)),
        ('XINERAMA', True),
    ],
    libraries=['X11', 'Xinerama', 'fontconfig', 'Xft'],
    library_dirs=['/usr/lib/x86_64-linux-gnu'],
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
        '/usr/include/X11/',
        '/usr/include/freetype2',
        DWM_SRC_ROOT_DIR,
    ],
    sources=[
        os.path.join(DWM_SRC_ROOT_DIR, 'drw.c'),
        os.path.join(DWM_SRC_ROOT_DIR, 'dwm.c'),
        os.path.join(DWM_SRC_ROOT_DIR, 'util.c'),
    ],
)


class BuildDwm(build_ext, object):
    user_options = build_ext.user_options + [
        ('dwm-source=', None, 'Path to DWM source')
    ]

    def initialize_options(self):
        super(BuildDwm, self).initialize_options()

    def copy_default_config(self):
        dest_file_path = relative_path(DWM_SRC_ROOT_DIR, 'config.h')
        if not os.path.exists(dest_file_path):
            source_file = open(
                relative_path('config.h'),
                'r'
            )
            dest_file = open(dest_file_path, 'w')
            dest_file.write(source_file.read())
            source_file.close()
            dest_file.close()

    def build_extension(self, ext):
        if ext.name == 'dwm':
            self.compiler = cc.new_compiler()
            self.copy_default_config()

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
