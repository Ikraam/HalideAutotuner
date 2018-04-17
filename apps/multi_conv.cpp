 

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
    
    const int sum_size = 400; // shared dimension between A and B 

        // Swizzle A for better memory order in the inner loop.
    Func A("A"), B("B"), Btmp("Btmp"), As("As"), Atmp("Atmp");
    Var k("k"), c("c"),z("z");
    Func prod("prod");
    Func result_("result_");
    Func AB("AB");
    RDom rv(0, 400);

    Halide::Buffer<float> A_ (8,400,20);
    Halide::Buffer<float> B_ (400,4096,20);
    Halide::Buffer<float> D_ (8,4096,20);
    Halide::Buffer<float> outputBuf;
    Halide::Buffer<float> outputBufNaive;
    int m,n,l;


    // img init 
    for(m=0; m<A_.dim(0).extent(); m++) {
    for(n=0; n<A_.dim(1).extent(); n++) {
    for(l=0; l<A_.dim(2).extent(); l++) {
      A_(m,n,l)=2;    
    }    
    }
    }
    
    for(m=0; m<B_.dim(0).extent(); m++) {
    for(n=0; n<B_.dim(1).extent(); n++) {
    for(l=0; l<B_.dim(2).extent(); l++) {
      B_(m,n,l)=1; 
    }   
    }    
    }

    for(m=0; m<D_.dim(0).extent(); m++) {
    for(n=0; n<D_.dim(1).extent(); n++) {
    for(l=0; l<D_.dim(2).extent(); l++) {
      D_(m,n,l)=1 + rand() % (( 255 + 1 ) - 1);   
      D_(m,n,l) = 0; 
    }
    }    
    }

    Func C_("C_");
    C_(i,j,c) = D_(i,j,c);
    AB(i,j,c) = D_(i,j,c);
    Atmp(i, j, c) = A_(i, j, c);  
    As(i, j, z, c) = Atmp(2*z + i, j,c);
    A(i, j, c) = As(i % 2, j, i / 2,c);
    Btmp(i, j, c) = B_(i, j, c);
    B(i, j, c) = Btmp(i, j, c);
    
    // Express all the products we need to do a matrix multiply as a 3D Func.
    prod(k, i, j, c) = A(i, k, c) * B(k, j, c);
    // Reduce the products along k.
    AB(i, j, c) += prod(rv, i, j, c);
    // Do the part that makes it a 'general' matrix multiply.
    result_(i, j, c) = AB(i, j, c);
 

    AUTOTUNE_HOOK(result_);
    // the schedule
    BASELINE_HOOK(result_);
    
    // test the validity of the schedule 
    bool scheduleValide = true;
    for(m=0; m<outputBuf.dim(0).extent(); m++) {
    for(n=0; n<outputBuf.dim(1).extent(); n++) {
    for(l=0; l<outputBuf.dim(2).extent(); l++) {
      if (outputBuf(m,n,l) != outputBufNaive(m,n,l)) {
         scheduleValide = false; 
         exit(-1);
        }
    }    
    }    
    } 
    if (scheduleValide == true){
      exit(0);
    }   
    return 0;
}
