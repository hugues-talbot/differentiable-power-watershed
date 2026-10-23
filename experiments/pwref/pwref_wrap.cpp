// Replacement main for Couprie's powerwatsegm (PW_1.0.1): same reading of the seed image
// and the same calls as src/powerwatsegm.c (algo 2), without the third-party argv parser
// (which miscompiles on current clang), with a choice of which weights go to the plateau
// routine, and raw dumps of everything.
//   pwref_wrap image.pgm seeds.pgm MODE OUTPREFIX LABELS SORT
//   MODE   prog : plateaus on the geodesically reconstructed weights, original weights inside
//                 (what the released program does by default)
//          geod : reconstructed weights for both (released program with -g 1)
//          raw  : original weights 255-|dI| for both (plain Algorithm 1 on the raw weights)
//   LABELS two  : seeds > 155 -> label 1, < 100 -> label 2 (README);  multi : value k>0 -> label k
//   SORT   stoch: stochastic quicksort (the program's choice);  bucket : bucket sort
// Outputs: OUTPREFIX.mask.u8 (N bytes, the mask image), OUTPREFIX.proba8.u8 (N bytes, the
// program's proba.pgm), OUTPREFIX.normal.u32 / .recon.u32 (M edge weights, the program's edge
// order), and, through the PW_DUMP_PROBA patch of MSF_RW.c, OUTPREFIX.proba.f32
// ((nb_labels-1) x N float32 potentials).  Prints the time of the PowerWatershed_q2 call.
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/time.h>
#include <mccodimage.h>
#include <mcimage.h>
#include <cccodimage.h>
#include <MSF_RW.h>
#include <powerwatsegm.h>

static double now() { struct timeval tv; gettimeofday(&tv, NULL); return tv.tv_sec + 1e-6 * tv.tv_usec; }

static void dump(const char *prefix, const char *suffix, const void *data, size_t nbytes) {
  char name[4096]; snprintf(name, sizeof name, "%s.%s", prefix, suffix);
  FILE *f = fopen(name, "wb"); if (!f) { perror(name); exit(1); }
  fwrite(data, 1, nbytes, f); fclose(f);
}

int main(int argc, char **argv) {
  if (argc < 7) {  fprintf(stderr, "usage: %s image.pgm seeds.pgm prog|geod|raw outprefix two|multi stoch|bucket\n", argv[0]); return 1; }
  char *image_name = argv[1], *seeds_name = argv[2], *mode = argv[3], *prefix = argv[4];
  bool mult = strcmp(argv[5], "multi") == 0;
  bool quicksort = strcmp(argv[6], "bucket") == 0;
  if (argc > 7) srand(atoi(argv[7]));   // seed of the stochastic quicksort (the program never seeds it)

  struct xvimage *seeds = readimage(seeds_name);
  if (!seeds) { fprintf(stderr, "readimage failed\n"); return 1; }
  unsigned char *s = UCHARDATA(seeds);
  int rs = rowsize(seeds), cs = colsize(seeds), ds = 1;
  int N = rs * cs * ds;
  int M = ds * rs * (cs - 1) + ds * (rs - 1) * cs + (ds - 1) * cs * rs;
  int *index_seeds = (int *)malloc(N * sizeof(int));
  uint8_t *index_labels = (uint8_t *)malloc(N * sizeof(uint8_t));
  int j = 0, nblabels;
  if (mult) {
    nblabels = 0;
    for (int i = 0; i < N; i++) if (s[i] > 0) { index_seeds[j] = i; index_labels[j] = s[i]; j++; if (s[i] > nblabels) nblabels = s[i]; }
  } else {
    nblabels = 2;
    for (int i = 0; i < N; i++) {
      if (s[i] > 155) { index_seeds[j] = i; index_labels[j] = 1; j++; }
      else if (s[i] < 100) { index_seeds[j] = i; index_labels[j] = 2; j++; }
    }
  }
  int size_seeds = j;
  freeimage(seeds);

  int **edges = (int **)malloc(2 * sizeof(int *));
  for (int i = 0; i < 2; i++) edges[i] = (int *)malloc(M * sizeof(int));
  compute_edges(edges, rs, cs, ds);

  uint32_t *weights = (uint32_t *)malloc(sizeof(uint32_t) * M);          // reconstructed
  uint32_t *normal_weights = grey_weights_PW(image_name, edges, index_seeds, size_seeds, weights, quicksort);
  dump(prefix, "normal.u32", normal_weights, sizeof(uint32_t) * M);
  dump(prefix, "recon.u32", weights, sizeof(uint32_t) * M);

  uint32_t *W, *NW;
  if (strcmp(mode, "prog") == 0) { W = weights; NW = normal_weights; }
  else if (strcmp(mode, "geod") == 0) { W = weights; NW = weights; }
  else if (strcmp(mode, "raw") == 0) { W = normal_weights; NW = normal_weights; }
  else { fprintf(stderr, "bad mode %s\n", mode); return 1; }

  char pname[4096]; snprintf(pname, sizeof pname, "%s.proba.f32", prefix);
  setenv("PW_DUMP_PROBA", pname, 1);
  struct xvimage *img_proba = allocimage(NULL, rs, cs, ds, VFF_TYP_1_BYTE);
  double t0 = now(); clock_t c0 = clock();
  struct xvimage *output = PowerWatershed_q2(edges, W, NW, 255, index_seeds, index_labels, size_seeds, rs, cs, ds, nblabels, quicksort, img_proba);
  double t1 = now(); clock_t c1 = clock();
  printf("pw_time %.4f cpu %.4f N %d M %d seeds %d labels %d\n", t1 - t0, (double)(c1 - c0) / CLOCKS_PER_SEC, N, M, size_seeds, nblabels);
  dump(prefix, "mask.u8", UCHARDATA(output), N);
  dump(prefix, "proba8.u8", UCHARDATA(img_proba), N);
  freeimage(output); freeimage(img_proba);
  free(weights); free(normal_weights); free(index_seeds); free(index_labels);
  return 0;
}
