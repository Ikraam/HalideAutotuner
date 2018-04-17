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

