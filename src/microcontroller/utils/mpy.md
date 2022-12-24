# Using mpy-cross

```
$ wget  https://adafruit-circuit-python.s3.amazonaws.com/bin/mpy-cross/mpy-cross.static-amd64-linux-8.0.0-beta.4-81-g295f7b490
$ chmod +x mpy-cross.static-amd64-linux-8.0.0-beta.4-81-g295f7b490
```

```
$ cat Dockerfile
FROM alpine
COPY mpy-cross.static-amd64-linux-8.0.0-beta.4-81-g295f7b490 /mpy-cross
```

```
$ docker build --tag mc .
```

```
$ ls /tmp/py
pico.py
```

```
$ docker run -it --entrypoint /bin/sh --volume /tmp/py:/py  mc
$ /mpy-cross --version
CircuitPython 8.0.0-beta.4-81-g295f7b490 on 2022-12-08; mpy-cross emitting mpy v5-CircuitPython
# cd /py
# /mpy-cross pico.py
# exit
$
```

```
$ ls /tmp/py
pico.py
pico.mpy
```

```
$ du -h pico.*
8.0K    pico.py
4.0K -h pico.mpy                                              
```
