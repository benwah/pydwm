import os
import ctypes


SO_PATH = os.path.join(
    os.path.dirname(__file__),
    '..',
    'dwm.so'
)


def init_dwm(*args):
    args = ['dwm'] + list(args)
    lib = ctypes.CDLL(SO_PATH)

    LP_c_char = ctypes.POINTER(ctypes.c_char)
    LP_LP_c_char = ctypes.POINTER(LP_c_char)

    lib.main.argtypes = (
        ctypes.c_int,
        LP_LP_c_char
    )

    argc = len(args)
    argv = (LP_c_char * (argc + 1))()

    for i, arg in enumerate(args):
        enc_arg = arg.encode('utf-8')
        argv[i] = ctypes.create_string_buffer(enc_arg)

    lib.main(argc, argv)
