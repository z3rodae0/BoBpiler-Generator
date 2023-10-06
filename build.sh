cd csmith_forkserver
cmake -S . -B build
cd build
make -j 4
mv ./src/csmith ./
cp ./csmith /bin/csmith_forkserver
cp ./csmith /usr/csmith_forkserver
cd ../../

cd yarpgen_forkserver
mkdir build && cd build
cmake ..
make -j 4
cp ./yarpgen /bin/yarpgen_forkserver
cp ./yarpgen /usr/bin/yarpgen_forkserver
cd ../../
