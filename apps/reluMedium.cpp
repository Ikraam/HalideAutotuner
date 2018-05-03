 

// On linux, you can compile and run it like so:
// g++ convolutionTensorFlow*.cpp -g -I ../../../include -I ../../../tools -L ../../../bin -lHalide `libpng-config --cflags --ldflags` -ljpeg -lpthread -ldl -o convolutionTensorFlow -std=c++11
// LD_LIBRARY_PATH=../../../bin ./convolutionTensorFlow


#include <Halide.h>

#define AUTOTUNE_HOOK(x)
#define BASELINE_HOOK(x)
using namespace Halide;

int main(int argc, char **argv) {


    // This code is a test code for the convolution 
    Func relu("relu");
    Func input("input");
    Halide::Buffer<float> in_img (64,64,32,32);
    Halide::Buffer<float> outputBuf;
    Halide::Buffer<float> outputBufNaive;
    int i,j,l,s;

    // img init 
    for(i=0; i<in_img.dim(0).extent(); i++) {
    for(j=0; j<in_img.dim(1).extent(); j++) {
    for(l=0; l<in_img.dim(2).extent(); l++) {
    for(s=0; s<in_img.dim(3).extent(); s++) {
      in_img(i,j,l,s)=1 + rand() % (( 255 + 1 ) - 1);
    }
    }    
    }    
    }
    
    Var x("x"), y("y"), c("c"), n("n");
    input(x,y,c,n) = in_img(x,y,c,n);
    relu(x,y,c,n) = Halide::max(0, input(x,y,c,n)); 
    
    AUTOTUNE_HOOK(relu);
    // the schedule
    BASELINE_HOOK(relu);
    
    // test the validity of the schedule    
    return 0;
}



















