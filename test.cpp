#include <Halide.h>
#include <HalideRuntime.h>
#include <HalideBuffer.h>
#include <stdio.h>
#include <sys/time.h>
#include <unistd.h>
#include <iostream>

#include <map>
#include <string>

// How many times to run (and take min)
// #define AUTOTUNE_TRIALS 3

// Limit in seconds to try running for (0 = no limit)
// #define AUTOTUNE_LIMIT 0

// Size to run with
//#define AUTOTUNE_N 1024, 1024




inline Halide::Buffer<TYPE_N> _autotune_timing_stub_original(Halide::Func& func, bool noAlarm) {
    func.compile_jit();

    // TODO: this assumes scalar/non-Tuple outputs - should generalize to a Realization
    // On cherche à trouver le buffer qui peut contenir les valeurs de la fonction de sortie  (taille et type) 
    std::vector<Halide::Type> out_types = func.output_types();
    std::vector<halide_buffer_t> out_raw_bufs;
    std::vector<Halide::Buffer<Halide::Type>> out_bufs;
/*
    for (int i = 0; i < out_types.size(); i++) {
        // Use the Buffer constructor as a helper to set up the buffer_t,
        // but then throw away its allocation which we don't really want.
        Halide::Buffer<buffer_t> bufinit(out_types[i], AUTOTUNE_N); // bufinit contient le types des sorties [je ne l'ai tjr pas compris)
        out_raw_bufs.push_back(*bufinit.raw_buffer()); // on rajoute à out_raw_bufs le buffer bufinit (le type de la sortie) . [push_back est une fonction C++ = rajoute un élément à la fin du vecteur]  
        out_raw_bufs[i].host = NULL;
        // TODO: free the host pointer?!
	Sortie fillOut;
        fillOut.typeSortie = out_types[i];
        fillOut.ss = &out_raw_bufs[i];
        out_bufs.push_back(fillOut);  //out_bufs contient les couples (type data, ...)
        assert(out_bufs[i].host_ptr() == NULL); // make sure we don't have an allocation
    }
    Halide::Realization output(out_bufs);
    func.infer_input_bounds(output); //pour une réalisation en sortie, on détermine la taille de toutes les images en entrée. 
    // assert(output[0].host_ptr()); // for now, the API doesn't seem to allocate outputs
    
    // TODO: this should go into Func::infer_input_bounds(Realization)
    for (int i = 0; i < output.size(); i++) {
        assert(!output[i].host_ptr()); // for now, the API doesn't seem to allocate outputs
        buffer_t buf = *output[i].raw_buffer();
        
        // Figure out how much memory to allocate for this buffer
        size_t min_idx = 0, max_idx = 0;
        for (int d = 0; d < 4; d++) {
            if (buf.stride[d] > 0) {
                min_idx += buf.min[d] * buf.stride[d];
                max_idx += (buf.min[d] + buf.extent[d] - 1) * buf.stride[d];
            } else {
                max_idx += buf.min[d] * buf.stride[d];
                min_idx += (buf.min[d] + buf.extent[d] - 1) * buf.stride[d];
            }
        }
        size_t total_size = (max_idx - min_idx);
        while (total_size & 0x1f) total_size++;

        // Allocate enough memory with the right dimensionality.
        Halide::Buffer buffer(output[i].type(), total_size,
                      buf.extent[1] > 0 ? 1 : 0,
                      buf.extent[2] > 0 ? 1 : 0,
                      buf.extent[3] > 0 ? 1 : 0);

        // Rewrite the buffer fields to match the ones returned
        for (int d = 0; d < 4; d++) {
            buffer.raw_buffer()->min[d] = buf.min[d];
            buffer.raw_buffer()->stride[d] = buf.stride[d];
            buffer.raw_buffer()->extent[d] = buf.extent[d];
        }
        
        output[i] = buffer;
    }*/
    int const x = func.dimensions();
    printf("\n ----------  hola x : %d---- \n", x);
    std::vector<int> dimensFunc;
    for(int i = 0; i < x; i++) {
      dimensFunc[i] = 4094;
    }



    timeval t1, t2;
    double rv = 0;
    const unsigned int timeout = AUTOTUNE_LIMIT;
    Halide::Buffer<TYPE_N> outputBuffer;
    if (noAlarm == false) {
    alarm(timeout); }
    for (int i = 0; i < AUTOTUNE_TRIALS; i++) {
      gettimeofday(&t1, NULL);
      outputBuffer = func.realize(dimensFunc);
      gettimeofday(&t2, NULL);
      if (noAlarm == false){
      alarm(0); } // disable alarm
      double t = (t2.tv_sec - t1.tv_sec) + (t2.tv_usec - t1.tv_usec)/1000000.0;
      if(i == 0 || t < rv)
        rv = t;
    }
    printf("{\"time\": %.10f}\n", rv);
    return outputBuffer;
}



inline Halide::Buffer<TYPE_N> _autotune_timing_stub(Halide::Func& func, bool noAlarm) {
    func.compile_jit();

    // TODO: this assumes scalar/non-Tuple outputs - should generalize to a Realization
    // On cherche à trouver le buffer qui peut contenir les valeurs de la fonction de sortie  (taille et type) 
    std::vector<Halide::Type> out_types = func.output_types();
    std::vector<Halide::Buffer<TYPE_N>> out_bufs;
    Halide::Buffer<TYPE_N> bufinit1;
    for (int i = 0; i < out_types.size(); i++) {
        // Use the Buffer constructor as a helper to set up the buffer_t,
        // but then throw away its allocation which we don't really want. 
        Halide::Buffer<TYPE_N> bufinit(AUTOTUNE_N); // 
	bufinit1 = bufinit;
        // TODO: free the host pointer?!
       out_bufs.push_back(bufinit);  //out_bufs contient les couples (type data, ...)
       //  je ne sais pas wech ndirou b hadi    assert(out_bufs[i].host_dirty() == NULL); // make sure we don't have an allocation */
    }
    Halide::Realization output(bufinit1);
    func.infer_input_bounds(output); 
    timeval t1, t2;
    double rv = 0;
    const unsigned int timeout = AUTOTUNE_LIMIT;
    Halide::Buffer<TYPE_N> outputBuffer;
    std::vector<double> trialsTime; 
    for (int i = 0; i < AUTOTUNE_TRIALS; i++) {
      if (noAlarm == false) {
      alarm(timeout); }
      gettimeofday(&t1, NULL);
      outputBuffer=func.realize(AUTOTUNE_N);
      gettimeofday(&t2, NULL);
      if (noAlarm == false) { 
      alarm(0);} // disable alarm
      double t = (t2.tv_sec - t1.tv_sec) + (t2.tv_usec - t1.tv_usec)/1000000.0;
      trialsTime.push_back(t);
      if(i == 0 || t < rv)
        rv = t;
    }
    std::sort(trialsTime.begin(), trialsTime.end());
    if (AUTOTUNE_TRIALS % 2 == 0) {rv= (trialsTime[AUTOTUNE_TRIALS / 2]+trialsTime[(AUTOTUNE_TRIALS / 2)-1])/2;}
    else {rv = trialsTime[(AUTOTUNE_TRIALS-1) / 2];}
    if (noAlarm == false){  
    printf("{\"time\": %.10f}\n", rv);}
    return outputBuffer;
}



#ifndef AUTOTUNE_HOOK
#define AUTOTUNE_HOOK(x)
#endif

#ifndef BASELINE_HOOK
#define BASELINE_HOOK(x)
#endif

 

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
    const int s = 8;
    const int sum_size = 500; // shared dimension between A and B 

        // Swizzle A for better memory order in the inner loop.
    Func A("A"), B("B"), Btmp("Btmp"), As("As"), Atmp("Atmp");
    Var k("k"), c("c"),z("z");
    Func prod("prod");
    Func result_("result_");
    Func AB("AB");
    RDom rv(0, 500);

    Halide::Buffer<float> A_ (1000,500);
    Halide::Buffer<float> B_ (500,2000);
    Halide::Buffer<float> D_ (1000,2000);
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
    {
        std::map<std::string, Halide::Internal::Function> funcs = Halide::Internal::find_transitive_calls((result_).function());
        outputBufNaive=_autotune_timing_stub(result_, true);
    }
    {
        std::map<std::string, Halide::Internal::Function> funcs = Halide::Internal::find_transitive_calls((result_).function());
        
         Var ii("ii");
         Var io("io");
         Var ji("ji");
         Var jo("jo");
         Var zi("zi");
         Var zo("zo");
         RVar rvi("rvi");
         RVar rvo("rvo");
         result_.tile(i, j ,io, jo ,ii, ji, 16, 16);
         As.split(j, jo , ji ,16);
         As.split(z, zo , zi ,16);
         AB.update(0).split(i, io , ii ,16);
         AB.update(0).split(rv, rvo , rvi ,16);
        As.reorder(zi,zo,ji,jo,i);
        AB.update(0).reorder(rvi,rvo,j,ii,io);
        result_.reorder(ii,ji,io,jo);As.parallel(i);AB.update(0).parallel(io);result_.parallel(jo);As.vectorize(ji);AB.update(0).vectorize(ii);result_.vectorize(ii);As.compute_at(AB,j);AB.compute_root();        
        outputBuf=_autotune_timing_stub(result_, false);
    } 
    ;
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
