 

// On linux, you can compile and run it like so:
// g++ convolutionTensorFlow*.cpp -g -I ../../../include -I ../../../tools -L ../../../bin -lHalide `libpng-config --cflags --ldflags` -ljpeg -lpthread -ldl -o convolutionTensorFlow -std=c++11
// LD_LIBRARY_PATH=../../../bin ./convolutionTensorFlow


#include <Halide.h>

#define AUTOTUNE_HOOK(x)
#define BASELINE_HOOK(x)
using namespace Halide;

int main(int argc, char **argv) {


    // This code is a test code for the convolution
    Var i("i"), j("j");
    //Var ti[3], tj[3];
    const int s = 5;
    const int sum_size = 10; // shared dimension between A and B 

        // Swizzle A for better memory order in the inner loop.
    Func A("A"), B("B"), Btmp("Btmp"), As("As"), Atmp("Atmp");
    Var k("k"), c("c"),z("z");
    Func prod("prod");
    Func result_("result_");
    Func AB("AB");
    RDom rv(0, 10);

    Halide::Buffer<float> A_ (100,10);
    Halide::Buffer<float> B_ (10,200);
    Halide::Buffer<float> D_ (100,200);
    Halide::Buffer<float> outputBuf;
    Halide::Buffer<float> outputBufNaive;
    int m,n,l;


    // img init 
    for(m=0; m<A_.dim(0).extent(); m++) {
    for(n=0; n<A_.dim(1).extent(); n++) {
      A_(m,n)=2;       
    }
    }
    
    for(m=0; m<B_.dim(0).extent(); m++) {
    for(n=0; n<B_.dim(1).extent(); n++) {
      B_(m,n)=1;    
    }    
    }

    for(m=0; m<D_.dim(0).extent(); m++) {
    for(n=0; n<D_.dim(1).extent(); n++) {
      D_(m,n)=1 + rand() % (( 255 + 1 ) - 1);   
      D_(m,n) = 0; 
    }    
    }

    Func C_("C_");
    C_(i,j) = D_(i,j);
    AB(i,j) = D_(i,j);
    Atmp(i, j) = A_(i, j);  
    As(i, j, z) = Atmp(s*z + i, j);
    A(i, j) = As(i % s, j, i / s);
    Btmp(i, j) = B_(i, j);
    B(i, j) = Btmp(i, j);
    
    // Express all the products we need to do a matrix multiply as a 3D Func.
    prod(k, i, j) = A(i, k) * B(k, j);
    // Reduce the products along k.
    AB(i, j) += prod(rv, i, j);
    // Do the part that makes it a 'general' matrix multiply.
    result_(i, j) = AB(i, j);
 

    AUTOTUNE_HOOK(result_);
    // the schedule
    BASELINE_HOOK(result_);
    
    // test the validity of the schedule 
    bool scheduleValide = true;
    for(m=0; m<outputBuf.dim(0).extent(); m++) {
    for(n=0; n<outputBuf.dim(1).extent(); n++) {
      if (outputBuf(m,n) != outputBufNaive(m,n)) {
         scheduleValide = false; 
         exit(-1);
        }
    }    
    } 
    if (scheduleValide == true){
      exit(0);
    }   
    return 0;
}
