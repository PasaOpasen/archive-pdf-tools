

prebuild:
	sudo dnf install make automake gcc gcc-c++ kernel-devel python-devel
	pip install numpy cythonbuilder==0.1.0

build:
	cybuilder init
	cybuilder build --include-numpy

	
