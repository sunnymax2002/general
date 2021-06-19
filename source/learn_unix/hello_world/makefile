# REF: https://flylib.com/books/en/2.131.1/building_a_simple_hello_world_application_with_gnu_make.html

# Syntax for a makefile
# targets: prerequisites
#		command-script

# This is the default target, which will be built when 
# you invoke make
# Here when 'make' is run, the target 'all' is invoked, which in turn invokes the target 'hello'
.PHONY: all
all: hello

# This rule tells make how to build hello from hello.c
hello: hello.c
	gcc -o hello hello.c

# This rule tells make to copy hello to the binaries subdirectory,
# creating it if necessary
.PHONY: install
install:
	mkdir -p binaries
	cp -p hello binaries

# This rule tells make to delete hello and hello.o
.PHONY: clean 
clean:
	rm -f hello