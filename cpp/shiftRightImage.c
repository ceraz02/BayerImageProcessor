/**
 * @file    shiftRightImage.c
 * @brief   Shift a region of a raw Bayer .bin image buffer to the right by a specified number of bytes.
 *
 * Used to correct misalignments in binary image data. Mimics the behavior of the Python version (shiftRightImage.py).
 *
 * Usage:
 *   shiftRightImage.exe img_file shift_count start_row [start_col [img_width img_height]]
 *
 * @author  Ahmad Asyraf Ahmad Saibudin
 * @date    2025-07-16
 * @version 1.0 (SEP 2025)
 *
 * @copyright
 * CSUG 2022-2025. All rights reserved.
 *
 * @note
 * Compilation: see Makefile in cpp/.
 *      make test_shiftRightImage.exe
 * Executable:  cpp/exe/test_shiftRightImage.exe
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <errno.h>

#define IMG_WIDTH 4096
#define FRAME_HEIGHT 4098

// Shift a region of the image buffer to the right by shift_count, 
// starting at (start_row, start_col)
int shiftImageRegion(
    uint8_t *buf, 
    int img_width, 
    int img_height, 
    int shift_count, 
    int start_row, 
    int start_col
) {
    if (shift_count < 1) {
        // snprintf(messageLogPrintf, LOG_MSG_SIZE,
        //         "ERROR 161 in shiftImageRegion: Invalid shift_count %d."
        //         " Must be >= 1.", shift_count);
        // printAndWriteToLog(messageLogPrintf, 1);
        // return 161;
        printf("ERROR in shiftImageRegion: Invalid shift_count %d."
               " Must be >= 1.\n", shift_count);
        return 1;
    }
    if (start_row < 0 || start_row >= img_height || 
        start_col < 0 || start_col >= img_width) {
        // snprintf(messageLogPrintf, LOG_MSG_SIZE,
        //         "ERROR 167 in shiftImageRegion: Invalid start_row/start_col"
        //         " (%d,%d).", start_row, start_col);
        // printAndWriteToLog(messageLogPrintf, 1);
        // return 167;
        printf("ERROR in shiftImageRegion: Invalid start_row/start_col"
               " (%d,%d).\n", start_row, start_col);
        return 1;
    }
    // Calculate the offset in the buffer to start shifting
    int offset = start_row * img_width + start_col;
    int total_pixels = img_width * img_height;
    if (offset < 0 || offset >= total_pixels) {
        // snprintf(messageLogPrintf, LOG_MSG_SIZE,
        //         "ERROR 168 in shiftImageRegion: Invalid offset (%d).", offset);
        // printAndWriteToLog(messageLogPrintf, 1);
        // return 168;
        printf("ERROR in shiftImageRegion: Invalid offset (%d).\n", offset);
        return 1;
    }
    int region_size = total_pixels - offset;
    if (shift_count < 1 || shift_count > region_size) {
        // snprintf(messageLogPrintf, LOG_MSG_SIZE,
        //         "ERROR 169 in shiftImageRegion: Invalid shift_count %d for region size %d.", shift_count, region_size);
        // printAndWriteToLog(messageLogPrintf, 1);
        // return 169;
        printf("ERROR in shiftImageRegion: Invalid shift_count %d for region size %d.\n", shift_count, region_size);
        return 1;
    }
    uint8_t *region = buf + offset;
    // Simple right shift, fill left with 0x00
    memmove(region + shift_count, region, region_size - shift_count);
    memset(region, 0x00, shift_count);
    return 0;
}

int main(int argc, char *argv[]) {

    if (argc != 4 && argc != 5 && argc != 7) {
        // printAndWriteToLog("", 0);
        // snprintf(messageLogPrintf, LOG_MSG_SIZE, 
        //             "USAGE: %s img_file shift_count start_row [start_col"
        //             " [img_width img_height]]", argv[0]);
        // printAndWriteToLog(messageLogPrintf, 0);
        printf("USAGE: %s img_file shift_count start_row [start_col"
               " [img_width img_height]]\n", argv[0]);
        return 1;
    }

    // Parse command line arguments
    const char *img_file = argv[1];
    int shift_count = atoi(argv[2]);
    int start_row = atoi(argv[3]);
    int start_col = (argc >= 5) ? atoi(argv[4]) : 0;
    int img_width = (argc == 7) ? atoi(argv[5]) : IMG_WIDTH;
    int img_height = (argc == 7) ? atoi(argv[6]) : FRAME_HEIGHT;
    if (shift_count < 1) {
        // snprintf(messageLogPrintf, LOG_MSG_SIZE, 
        //             "ERROR 161 in shiftRightImage: Invalid shift_count %d."
        //             " Must be >= 1.", shift_count);
        // printAndWriteToLog(messageLogPrintf, 1);
        // return 161;
        printf("ERROR in shiftRightImage: Invalid shift_count %d."
               " Must be >= 1.\n", shift_count);
        return 1;
    }
    if (start_row < 0 || start_row >= img_height || 
        start_col < 0 || start_col >= img_width) {
        // snprintf(messageLogPrintf, LOG_MSG_SIZE,
        //         "ERROR 167 in shiftRightImage: Invalid start_row/start_col"
        //         " (%d,%d).", start_row, start_col);
        // printAndWriteToLog(messageLogPrintf, 1);
        printf("ERROR in shiftRightImage: Invalid start_row/start_col"
               " (%d,%d).\n", start_row, start_col);
        return 1;
    }

    // Open image file
    FILE *fd = fopen(img_file, "rb+");
    if (!fd) {
        // snprintf(messageLogPrintf, LOG_MSG_SIZE, 
        //         "ERROR 6 in shiftRightImage: Could not open file"
        //         " %s - %s", img_file, strerror(errno));
        // printAndWriteToLog(messageLogPrintf, 1);
        printf("ERROR in shiftRightImage: Could not open file"
               " %s - %s\n", img_file, strerror(errno));
        return 1;
    }

    // Get file size
    fseek(fd, 0, SEEK_END);
    long fsize = ftell(fd);
    fseek(fd, 0, SEEK_SET);
    if (fsize != img_width * img_height) {
        // snprintf(messageLogPrintf, LOG_MSG_SIZE, 
        //         "ERROR 9 in shiftRightImage: Incorrect file size"
        //         " for %s: %ld != expected %d", 
        //         img_file, fsize, img_width * img_height);
        // printAndWriteToLog(messageLogPrintf, 1);
        printf("ERROR in shiftRightImage: Incorrect file size"
               " for %s: %ld != expected %d\n", 
               img_file, fsize, img_width * img_height);
        fclose(fd);
        return 1;
    }

    // Allocate buffer for image data
    uint8_t *buf = malloc(fsize);
    if (!buf) {
        // snprintf(messageLogPrintf, LOG_MSG_SIZE, 
        //         "ERROR 12 in shiftRightImage: Failed to allocate"
        //         " memory for %s", img_file);
        // printAndWriteToLog(messageLogPrintf, 1);
        printf("ERROR in shiftRightImage: Failed to allocate"
               " memory for %s\n", img_file);
        fclose(fd);
        return 1;
    }

    // Read image data to buffer
    size_t bytesRead = fread(buf, 1, fsize, fd);
    if (bytesRead != (size_t)fsize) {
        // snprintf(messageLogPrintf, LOG_MSG_SIZE, 
        //         "ERROR 162 in shiftRightImage: Read failure or incomplete"
        //         " read from file %s. Read %zu bytes instead of %ld", 
        //         img_file, bytesRead, fsize);
        // printAndWriteToLog(messageLogPrintf, 1);
        printf("ERROR in shiftRightImage: Read failure or incomplete"
               " read from file %s. Read %zu bytes instead of %ld\n", 
               img_file, bytesRead, fsize);
        free(buf);
        fclose(fd);
        return 1;
    }

    // Shift the image region
    int result = shiftImageRegion(buf, img_width, img_height, shift_count, start_row, start_col);
    if (result != 0) {
        printf("ERROR in shiftRightImage: shiftImageRegion failed with error code %d\n", result);
        free(buf);
        fclose(fd);
        return result;
    }

    fseek(fd, 0, SEEK_SET);
    fwrite(buf, 1, fsize, fd);
    fflush(fd);

    free(buf);
    fclose(fd);
    printf("Successfully shifted image region in %s\n", img_file);
    return 0;
}