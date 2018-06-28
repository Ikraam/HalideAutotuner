 

// On linux, you can compile and run it like so:
// g++ convolutionTensorFlow*.cpp -g -I ../../../include -I ../../../tools -L ../../../bin -lHalide `libpng-config --cflags --ldflags` -ljpeg -lpthread -ldl -o convolutionTensorFlow -std=c++11
// LD_LIBRARY_PATH=../../../bin ./convolutionTensorFlow


#include <Halide.h>

#define AUTOTUNE_HOOK(x)
#define BASELINE_HOOK(x)
using namespace Halide;

int main(int argc, char **argv) {


    // This code is a test code for the convolution 
    Func max_pooled("max_pooled"); 
    Func input("input");
    Halide::Buffer<float> in_img (256,256,32,32);
    Halide::Buffer<float> outputBuf;
    Halide::Buffer<float> outputBufNaive;
    int i,j,l,s;
    int pool_size = 4;


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
    RDom rp(0, pool_size, 0, pool_size);
    max_pooled(x, y, c, n) = maximum(input(pool_size * x + rp.x, pool_size * y + rp.y, c, n));

    AUTOTUNE_HOOK(max_pooled);
    // the schedule
    BASELINE_HOOK(max_pooled);
    
    // test the validity of the schedule 
    bool scheduleValide = true;
    for(i=0; i<outputBuf.dim(0).extent(); i++) {
    for(j=0; j<outputBuf.dim(1).extent(); j++) {
    for(l=0; l<outputBuf.dim(2).extent(); l++) {
    for(s=0; s<outputBuf.dim(3).extent(); s++) {
      if (outputBuf(i,j,l,s) != outputBufNaive(i,j,l,s)) {
         scheduleValide = false; 
         exit(-1);
        }
    }
    }    
    }    
    } 
    if (scheduleValide == true){
      exit(0);
    }   
    return 0;
}
