 

// On linux, you can compile and run it like so:
// g++ convolutionTensorFlow*.cpp -g -I ../../../include -I ../../../tools -L ../../../bin -lHalide `libpng-config --cflags --ldflags` -ljpeg -lpthread -ldl -o convolutionTensorFlow -std=c++11
// LD_LIBRARY_PATH=../../../bin ./convolutionTensorFlow


#include <Halide.h>

#define AUTOTUNE_HOOK(x)
#define BASELINE_HOOK(x)
using namespace Halide;

int main(int argc, char **argv) {


    // This code is a test code for the convolution 
    Func conv("conv");
    Func input("input");
    Func infilter("infilter");
    Func bias("bias");
    Func relu("relu");
    Halide::Buffer<float> in_img (131,131,64,4);
    Halide::Buffer<float> in_filter (3,3,64,64);
    Halide::Buffer<float> in_bias (64);
    Halide::Buffer<float> outputBuf;
    Halide::Buffer<float> outputBufNaive;
    int i,j,l,s;

    // bias init 
    for(i=0; i<in_bias.dim(0).extent(); i++) {
    in_bias(i) = 1 + rand() % (( 255 + 1 ) - 1);    
    }

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
    // init filter
    for(i=0; i<in_filter.dim(0).extent(); i++) {
    for(j=0; j<in_filter.dim(1).extent(); j++) {
    for(l=0; l<in_filter.dim(2).extent(); l++) {
    for(s=0; s<in_filter.dim(3).extent(); s++) {
      in_filter(i,j,l,s)=1 + rand() % (( 255 + 1 ) - 1);
    }
    }    
    }    
    }
    
    Var x("x"), y("y"), c("c"), z("z"), n("n");
    bias(z) = in_bias(z);
    infilter(x,y,c,z) = in_filter(x,y,c,z);
    input(x,y,c,n) = in_img(x,y,c,n);
    conv(x,y,z,n) = bias(z);   
    Halide::RDom r(0,3 ,0, 3, 0, 64);
    conv(x,y,z,n) =  Halide::cast<float>(conv(x,y,z,n) + infilter(r.x,r.y,r.z,z)*input(x + r.x, y + r.y, r.z,n)); 
    relu(x,y,z,n) = Halide::max(0,conv(x,y,z,n));

    AUTOTUNE_HOOK(relu);
    // the schedule
    BASELINE_HOOK(relu);
    
    // test the validity of the schedule 
   /* bool scheduleValide = true;
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
    }*/
    float code = 0.0f;
    /*for(m=0; m<outputBuf.dim(0).extent(); m++) {
    for(n=0; n<outputBuf.dim(1).extent(); n++) {
      code = code + outputBuf(m,n);
      somme_ten=somme_ten+1;
      if (somme_ten == 10)
      {
        somme_ten = 1;
        code = (int)code % 10;
      }
    }    
    }*/
    printf("{\"code\": %.10f, \"time\": %.10f }\n", code, time);   
    return 0;
}
