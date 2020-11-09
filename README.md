![demo](screenshot.gif)

# NES Punchout AI

LSTM Network trained to play [Punchout](https://en.wikipedia.org/wiki/Punch-Out!!_(NES)), a game released for the NES (Nintendo Entertainment System). This bot uses [pykitml](https://github.com/RainingComputers/pykitml) ML library.

## Running

### Install requirements

```python3 -m pip install -r requirements.txt```

(Note: You may have to use `python` instead of `python3` for windows)

### Install FCEUX NES Emulator and Lua Socket

Ubuntu/Debian

```
sudo apt-get install fceux
sudo apt-get install lua5.1-socket
```

Windows

http://fceux.com/web/download.html

http://files.luaforge.net/releases/luasocket/luasocket/luasocket-2.0.2/luasocket-2.0.2-lua-5.1.2-Win32-vc8.zip

(Copy Lua socket files to FCEUX's directory, say yes to replace files)


### Run 

Ubuntu/Debian

+ Start script, `python3 bot.py`

+ Start Fceux

+ Option > Video Config > Set X and Y Scale to 2.0

+ File > Open ROM, browse to `punchout_rom.nes`

+ File > Load Lua Script, browse to `fceux_client.nes`

+ Place the FCEUX window on TOP RIGHT CORNER

Windows

+ Start script, `python3 bot.py`

+ Start FCEUX

+ Config > Video > Window Settings > Set X and Y Scale to 2.0

+ File > Open ROM, browse to `punchout_rom.nes`

+ File > Lua > New Lua Script Window, browse to `punchout_rom.nes`, click Run

+ Place the FCEUX window on TOP RIGHT CORNER

(Note: You may have to use `python` instead of `python3` for windows)
