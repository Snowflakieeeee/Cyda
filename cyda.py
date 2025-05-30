#!/usr/bin/env python3

import shlex, sys, os
from time import time as stopwatch
import random

motivating_sentences = [
	"The disappointment of the gods is palpable",
	"Tsk tsk, Claude is coming",
	"Make it work or an LLM is gonna take your job",
	"I believe in you!",
	"GIT GUD",
	"........",
	"And you thought that would work?!?",
	"Remember that deadline? Yep, time to move it again.",
	"Remember that deadline? Yep, time to forget it.",
	"My LLM could write better code than that (I have no LLM)",
	"Forgot the semi-colon again? Sigh.",
	"Got a 19 page thesis summary of your template instantiation error? Sigh."
]
motivating_sentence = random.choice(motivating_sentences)

COMPILER = ""
FLAGS = ""
FILES = []
INCLUDE_PATHS = []
EXECUTABLE = None

def red(str):
	return f"\x1b[31m{str}\x1b[0m"

def green(str):
	return f"\x1b[32m{str}\x1b[0m"

def yellow(str):
	return f"\x1b[33m{str}\x1b[0m"

def read_cydafile():
	i = 1
	global COMPILER, FLAGS, FILES, INCLUDE_PATHS, EXECUTABLE
	if "cydafile" in os.listdir("."):
		for line in open("./cydafile", "r").readlines():
			command = shlex.split(line)
			if not len(command) > 0: continue
			# print(command)
			match command[0]:
				case "//":
					continue
				case "compiler":
					try:
						COMPILER = command[1]
					except:
						raise RuntimeError(f"Error on line {i}. Compiler not specified. Exiting...")
						sys.exit(1)

				case "include":
					try:
						path = command[1]
					except:
						raise RuntimeError(f"Error on line {i}. Did you forget to add a include path? Exiting...")
					INCLUDE_PATHS.append(path)

				case "flags":
					FLAGS = " ".join([flag for flag in command[1:]])
				
				case "file":
					try:
						FILES.append(command[1])
					except:
						raise RuntimeError(f"Error on line {i}. File name not specified. Exiting...")
						sys.exit(1)

				case "exec":
					if EXECUTABLE != None:
						raise RuntimeError(f"Error on line {i}. Executable name already set to {EXECUTABLE}.\nPlease mention only one executable name. Exiting...")
						sys.exit(1)
					else:
						try:
							EXECUTABLE = command[1]
						except:
							raise RuntimeError(f"Error on line {i}. Executable name not specified. Exiting...")
			i+=1

		if COMPILER == "":
			raise RuntimeError("Compiler not set. Exiting...")
		if len(FILES) == 0:
			raise RuntimeError("No files given. Exiting...")
		if EXECUTABLE == None:
			raise RuntimeError("Executable name not set. Exiting...")
	else:
		raise RuntimeError("Uh, cydafile isn't found in this directory. Exiting...")


commands = sys.argv[1:]


def build():
	start = stopwatch()
	read_cydafile()

	total = len(FILES)
	success = 0
	obj_files = []
	for file in FILES:
		fn = file.split(".")[0]
		obj_files.append(f"{fn}.o")
		exit_code = os.system(f"{COMPILER} {FLAGS} {' '.join(f'-I{d}' for d in INCLUDE_PATHS)} -c {file} -o {fn}.o")
		if exit_code == 0:
			success += 1

	end = stopwatch()

	print("\n-------------------------------------------")
	print(f"DURATION: {round(end-start, 3)}s")
	print(green(f"OK: {success}/{total}"))

	if success == total:
		print(green(f"OK: ({total-success}/{total})"))
		os.system(f"{COMPILER} {' '.join(f'-I{d}' for d in INCLUDE_PATHS)} {" ".join(obj_files)} -o {EXECUTABLE}")
	else:
		print(red(f"FAILED: {total-success}/{total}"))
		print(yellow(motivating_sentence))

def run():
	start = stopwatch()
	read_cydafile()

	total = len(FILES)
	success = 0
	obj_files = []
	for file in FILES:
		fn = file.split(".")[0]
		obj_files.append(f"{fn}.o")
		exit_code = os.system(f"{COMPILER} {FLAGS} {' '.join(f'-I{d}' for d in INCLUDE_PATHS)} -c {file} -o {fn}.o")
		if exit_code == 0:
			success += 1
	
	end = stopwatch()
	print("\n-------------------------------------------")
	print(f"DURATION: {round(end-start, 3)}s")
	print(green(f"OK: {success}/{total}"))

	if success == total:
		print(green(f"No failed compiles ({total-success}/{total}). Hurray!"))
		os.system(f"{COMPILER} {' '.join(f'-I{d}' for d in INCLUDE_PATHS)} {" ".join(obj_files)} -o {EXECUTABLE}")
		print("-------------------------------------------\n")
		os.system(f"./{EXECUTABLE}")
	else:
		print(red(f"FAILED: {total-success}/{total}"))
		print(yellow(motivating_sentence))


def clean():
	os.system("rm -f ./*.o")
	read_cydafile()
	for file in FILES:
		objfilename = file.split(".")[0]
		os.system(f"rm -f ./{objfilename}.o")


def generate_makefile():
	read_cydafile()
	with open("Makefile", "w+") as file:
		file.truncate(0)
		
		# COMPILERS AND FLAGS
		file.writelines([
			f"CC = {COMPILER}\n",
			f"CFLAGS = {FLAGS}\n",
			"\n",  
		])


		# FILE RULES
		for f in FILES:
			splitfilename = f.split(".")
			objfilename = splitfilename[0].split("/")
			objfilename = objfilename[len(objfilename) - 1]
			print(splitfilename[0], objfilename)
			file.write(f"\n{objfilename}.o: {f}\n	$(CC) $(CFLAGS) {' '.join(f'-I{d}' for d in INCLUDE_PATHS)} -c {splitfilename[0]}.c -o {objfilename}.o\n")
		file.write("\n")

		# FINAL EXECUTABLE RULE
		file.write(f"{EXECUTABLE}: ")   
		for f in FILES:
			splitfilename = f.split(".")
			objfilename = splitfilename[0].split("/")
			objfilename = objfilename[len(objfilename) - 1]
			
			file.write(f"{objfilename}.o ")
			
		file.write("\n	$(CC) ")
		
		for f in FILES:
			splitfilename = f.split(".")
			objfilename = splitfilename[0].split("/")
			objfilename = objfilename[len(objfilename) - 1]
			
			file.write(f"{objfilename}.o ")
			
		file.write(f"{' '.join(f'-I{d}' for d in INCLUDE_PATHS)} -o {EXECUTABLE}\n")

		
		# CLEAN AND RUN RULES
		file.write("clean: \n")
		file.write(f"	rm -f *.o {EXECUTABLE}\n")

		file.write("run:\n")
		file.write(f"	make {EXECUTABLE}\n")
		
	print(green("If you see this message, your makefile is ready!"))

def new_project(name, projtype, compiler_name):
	if projtype not in ["-c", "-cpp", "-c++", "-cxx"]:
		raise RuntimeError(red(f"I don't know the specified project type {projtype} D:"))
	
	if compiler_name not in ["gcc", 'g++', 'clang', 'clang++']:
		i = input("I dont know the given compiler. Are you sure you want to proceed? (You can change the compiler later in the cydafile) [y/N]:")
		if i == "n" or not i:
			raise RuntimeError(red("Unrecognised compiler. Exiting..."))
	
	os.makedirs(f"./{name}/libs")
	os.makedirs(f"./{name}/src")
	if projtype == "-c":
		if compiler_name in ["g++", "clang++"]:
			print(red("Incompatible compiler for cxx used. Using fallback gcc"))
		compiler_name = "gcc"
		
		with open(f"{name}/src/main.c", "w+") as file:
			file.writelines([
				"#include <stdio.h>\n"
				"#include \"lib.h\"      // Cyda manages include paths! no need to specify!\n"
				"\n",
				"int main(){\n"
				"	printf(\"Hello Cyda!\\n\");\n",
				"	hello_from_lib();\n"
				"	return 0;\n",
				"}\n"
			])

		with open(f"{name}/libs/lib.c", "w+") as file:
			file.writelines([
				"#include <stdio.h>\n"
				"\n",
				"void hello_from_lib(){\n"
				"	printf(\"Hi there!\\n\");\n"
				"}\n"
			])

		with open(f"{name}/libs/lib.h", "w+") as file:
			file.writelines([
				"#pragma once\n",
				"\n",
				"void hello_from_lib();\n"
			])
		
		with open(f"{name}/cydafile", "w+") as file:
			file.writelines([
				f"compiler {compiler_name}\n",
				"flags -Wall \n",
				"// Turning on warnings, Write good code for the sake of Torvalds, okay?\n",
				"include libs\n",
				"// This is also a flag, it sets -I\n",
				" \n",
				"// BTW, // itself is a command, for comments :p\n",
				"file src/main.c\n",
				"file libs/lib.c   // explicit path to be given\n",
				f"exec {name}\n"
			])

	elif projtype != "-c":
		if compiler_name in ["gcc", "clang"]:
			print(red("Incompatible compiler for cxx used. Using fallback g++"))
		
		compiler_name = "g++"
		with open(f"{name}/src/main.cpp", "w+") as file:
			file.writelines([
				"#include <iostream>\n"
				"#include \"lib.h\"      // Cyda manages include paths! no need to specify!\n"
				" \n",
				"int main(){\n"
				"	std::cout << \"Hello from Cyda!\" << std::endl;\n",
				"	std::cout << add_from_lib(3,5) << \"\\n\" << std::endl;\n",
				"	return 0;\n",
				"}\n"
			])

		with open(f"{name}/libs/lib.cpp", "w+") as file:
			file.writelines([
				"#include <iostream>\n",
				"\n",
				"int add_from_lib(int a, int b){\n",
				"	return a + b;\n",
				"}\n",
			])

		with open(f"{name}/libs/lib.h", "w+") as file:
			file.writelines([
				"#pragma once\n",
				" \n",
				"int add_from_lib(int, int);\n"
			])
		
		with open(f"{name}/cydafile", "w+") as file:
			file.writelines([
				f"compiler {compiler_name}\n",
				"flags -Wall   \n",
				"// Turning on warnings, Write good code for the sake of Torvalds, okay?\n" 
				"include libs   ",
				"// This is also a flag, it sets -I\n"
				" \n",
				"// BTW, // itself is a command, for comments :p\n",
				"file src/main.cpp\n",
				"file libs/lib.cpp   // explicit path to be given\n",
				f"exec {name}\n"
			])
	print(green(f"Project creation complete with name {name}!"))

if len(commands) == 0:	
	print("Use --help for, you guessed it, getting help.")
	sys.exit(1)

match commands[0]:
	case "--help":
		print("Use --help to get this message")
		print("Use --build to build but not run the executable")
		print("Use --run to build the files, clear the screen, and run the executable immediately")
		print("Use --clean to clean the .o files generated")
		print("Use --new <project name> to create a new template project. use -c or -cpp/-cxx/-c++ to specify project language type.\n	Optionally, specify the compiler using --compiler gcc/clang/clang++/g++/etc. By default cyda uses gcc/g++ :D")
		print("Use --makefile to generate a makefile for the given cyda script")
	case "--build":
		build()
	case "--run":
		run()
	case "--clean":
		clean()
	case "--makefile":
		generate_makefile()
	case "--new":
		try:
			name = commands[1]
		except:
			print(red("Name of project not specified. Exiting..."))
			sys.exit(1)
		try:
			_type = commands[2]
		except:
			print(red("Project type (C/C++) not specified. Exiting..."))
			sys.exit(1)
		
		try:
			compiler_name = commands[3]
		except:
			if _type == "-c":
				compiler_name = "gcc"
			else:
				compiler_name = "g++"

		new_project(name, _type, compiler_name)


