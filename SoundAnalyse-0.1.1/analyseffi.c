#include <Python.h>
#include <stdlib.h>
#include <limits.h>

/* Copyright 2008, Nathan Whitehead
   Released under the LGPL
*/

static PyObject *detect_pitch(PyObject *self, PyObject *args)
{
  char *data;
  signed short int *data2, *datao1, *datao2;
  int len;
  float min_frequency, max_frequency, samplerate, sens, ratio;
  int max_period, min_period;
  int *amd;
  int o, sum, i, d;
  int minval, maxval;
  int cutoff;
  int search_length;
  int minpos;


  /* Use AMDF strategy
     AMDF (average magnitude difference function)
     Slide data along itself different distances (periods)
     then calculate the AMD.  Find trough in AMD to get period of pitch.
  */
  if (!PyArg_ParseTuple(args, "s#fffff", 
                        &data, &len, 
                        &min_frequency, 
                        &max_frequency, 
                        &samplerate, 
                        &sens,
                        &ratio))
      return NULL;


  Py_BEGIN_ALLOW_THREADS;
  

  /* coerce char* into short* */
  data2 = (signed short int *)data;

  /* Longest period we can detect */
  max_period = (int)(samplerate / min_frequency + 0.5);
  /* Shortest period we can detect */
  min_period = (int)(samplerate / max_frequency + 0.5);
  /* amd is an integer array that holds average magnitude differences
  for each offset value 
  */

  amd = (int *)malloc(sizeof(int) * (max_period + 1)); 
  /* add one so amd[max_period] is allowed */
  if(!amd) return NULL;

  /* Try each offset from min to max and calculate amd */  
  for(o=min_period; o<=max_period; o++) {
      /* This section is an attempt to be fast in C
         so no function calls, uses incremented pointers
         and pointer arithmetic
      */
      sum = 0;
      datao1 = data2;
      datao2 = data2 + o;
      for(i=0; i<len/2 - o; i++) {
          d = *(datao1++) - *(datao2++);
          if(d<0) d = -d;
          sum += d;
      }
      amd[o] = sum;
  }

  /* To get pitch, we want to find FIRST minimum
     First find smallest value (deepest minimum)
     Can't just use this as answer since higher pitches have multiple troughs
     Deepest one might be wrong octave (deepest one jumps around randomly)
  */
  /* Find minimum and maximum values in amd 
     We will use these to determine where to look for "low" troughs
  */
  minval = INT_MAX;
  maxval = INT_MIN;
  for(o=min_period; o<=max_period; o++) {
      if(amd[o] < minval) minval = amd[o];
      if(amd[o] > maxval) maxval = amd[o];
  }
  /* The threshold will be slightly higher than lowest trough,
     where the amount to raise is sens percentage of max-min.
     If sens=0, we will only get the lowest trough.
     If sens=0.1, we get all troughs in the lowest 10% of range
     between lowest trough and highest peak.
     Lower values of sens are more prone to octave skipping
     If values are too high can miss troughs altogether.
  */
  cutoff = (int)(sens * ((float)(maxval - minval))) + minval;
  /* Now find first value that is within the sensitivity range */
  o = min_period;
  while(o<=max_period && (amd[o] > cutoff)) o++;

  /* Now o holds value that is close to true first trough position
     but it will be a little early (because cutoff is higher that trough).
     Still need to do a small search to find best value of pitch.
     Find minimum over next bunch of values.
     Don't want to search too far, might get second trough.
  */
  search_length = min_period / 2;
  minval = amd[o];
  minpos = o;
  for(i=o; (i<o+search_length) && (i<=max_period); i++) {
      if(amd[i] < minval) {
          minval = amd[i];
          minpos = i;
      }
  }

  Py_END_ALLOW_THREADS;

  /* How do we know whether we got a pitch or not?
     Compare amd at detected pitch with max amd.
     If maxval is ratio times bigger or more, we know we got a pitch.
  */
  if((int)(amd[minpos] * ratio) < maxval) {
      // Got a pitch  
      free(amd);
      return Py_BuildValue("i", minpos);
  }
  free(amd);
  Py_RETURN_NONE;
}

PyMethodDef methods[] = {
    {"detect_pitch", detect_pitch, METH_VARARGS, "Detect fundamental pitch"},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC 
initanalyseffi(void)
{
    (void) Py_InitModule("analyseffi", methods);
}
