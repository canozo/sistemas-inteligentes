# What Do You Mean?

Necesario correr en un ambiente Linux (para soportar los comandos) y tener sqlite3 para C.

1. Crear el archivo wdym.db para crear la tabla
```
$ sqlite3 wdym.db
> create table meanings (said varchar(15), meant varchar(15));
```

2. Compilar
```
$ make
```

3. Correr
```
$ ./main.out wdym.db
```
