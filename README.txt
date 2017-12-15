## What is this?

This is a simple python wrapper around `dwm`.

It compiles `dwm` as a shared library, provides a `pydwm` module and a `pydwm` console script that calls `pydwm`'s `init_dwm` function.

## Why?

The main reason for doing this is to faciliate creating a startup script for DWM, without having to add something like adding `python my_scripy.py & dwm` to `~/.xinitrc`, which results in some lingering processes when logging out.

With this, you can start `dwm` from a python script, and spawn sub-processes / threads or whatever you want.
