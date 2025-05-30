Note: This was just a personal script/utility I wrote for myself within a day, but I will refactor the code later for general readability since I am pushing this to open source.

# Cyda
Cyda is a *much* simpler build system for C/C++. Designed after feeling lazy to write Makefiles for each new project. 

Whenever I started a new project in C/C++, I would always manually create folders to organize my code and then finally, create the Makefile. 
Here is what my makefile would *generally* look like at the start of a brand new project
```make
CC = gcc
CFLAGS = -Wall -Ilib
OBJ = lib/lib1.o lib/lib2.o
TARGET = main

all: $(TARGET)

$(TARGET): $(OBJ) src/main.o
	$(CC) -o $@ $^

lib/lib1.o: lib/lib1.c lib/lib1.h
	$(CC) $(CFLAGS) -c $< -o $@

lib/lib2.o: lib/lib2.c lib/lib2.h
	$(CC) $(CFLAGS) -c $< -o $@

src/main.o: src/main.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f lib/*.o src/*.o $(TARGET)
```
Multiple symbols like $<, $@, $^, etc. Although some of you may say 'just learn it, you'll get used to it', but *i was lazy.*

Here is another version using wildcard, its more dynamic, but still *slightly* messy
```make
CC = gcc
CFLAGS = -Wall -Ilib
SRCS = $(wildcard lib/*.c src/*.c)
OBJS = $(SRCS:.c=.o)
TARGET = main

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) -o $@ $^

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f lib/*.o src/*.o $(TARGET)
```

Here is what my *cydafile* looks like in new projects now:
```
compiler gcc
flags -Wall
// include lib => -Ilib
include lib
// Target main
exec main

// You'll notice that the header file for the c files are not given, cyda assumes that lib1.c has a coresponding lib1.h since its standard
file lib/lib1.c
file lib/lib2.c
file src/main.c
// This is like ~50% smaller than the makefile at the start of this readme!
```
Aaand you're done! 
No rules needed for .o, or cleaning the .o files later

Here is how it works -- 
```
$ cyda --help
Use --help to get this message
Use --build to build but not run the executable
Use --run to build the files, clear the screen, and run the executable immediately
Use --clean to clean the .o files generated
Use --new <project name> to create a new template project. use -c or -cpp/-cxx/-c++ to specify project language type.
	Optionally, specify the compiler using --compiler gcc/clang/clang++/g++/etc. By default cyda uses gcc/g++ :D
Use --makefile to generate a makefile for the given cyda script
```
When a `cydafile` is detected in the working directory, you can run `--build` and `--run` to do their respective jobs, according to the script in the cydafile.
and `--clean` uses the cydafile once again to see where the `*.o` files *would* be generated and then automatically delete them. Thats why there is no rule for `--clean`

`--new <project name> -c/c++/cxx/cpp --compiler gcc/clang/g++/clang++` is the concept I borrowed from cargo, because once again, I was quite tired of setting up manually my folder structure. It automatically creates a new folder named `<project name>` with starter files for `C/C++` according to the flag and then optionally, you can specify the compiler. 
The folder structure it generates is quite standard --
```
PROJECT_NAME
  | --- libs/
  |       | --- lib1.c  / or lib1.cpp
  |       | --- lib1.h
  |
  | --- src/
  |       | --- main.c  / or main.cpp 
  |
  | --- cydafile
```
And the cydafile generated matches the folder structure already. 


## NOTE -
Currently some features are missing which I will add in the future - 
  * Ability to control where the output object files are located, although I wont add granular control for per file
  * Ability to control where the output executable file is generated
  * Ability to add wildcard like `*.c` to dynamically add files to the compilation without needing to specify each one
  * More *motivating* quotes in the future (you'll know when you use --run/--build)
  
May or may not add support for assembly (linux only)

