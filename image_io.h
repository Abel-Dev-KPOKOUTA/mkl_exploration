#ifndef IMAGE_IO_H
#define IMAGE_IO_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Structure pour stocker une image
typedef struct {
    int width;
    int height;
    int max_value;
    double *data;
} Image;

// Prototypes des fonctions
Image* image_create(int width, int height);
void image_free(Image *img);
Image* image_load_pgm(const char *filename);
int image_save_pgm(const char *filename, Image *img);
Image* image_copy(Image *src);
void image_normalize(Image *img);

#endif // IMAGE_IO_H


