#include <stdio.h>
#include <unistd.h>
#include <math.h>

#include "matmult.h"


//////////////// Original Code ////////////////
/* void matmult(short int A[N][N],short int B[N][N],int C[N][N]){
	int i, j, k;
    int sum = 0;
    
	for (i = 0; i < N; i++){
        for(j = 0; j < N; j++){
            for(k = 0; k < N; k++){
                sum += A[i][k] * B[k][j];
            }
            C[i][j] = sum;
            sum = 0;
        }
    }
} */

//////////////// [Op1: Use unroll pragma to minimize loop times] ////////////////
void matmult(short int A[N][N],short int B[N][N],int C[N][N]){
	int i, j, k;
    int sum = 0;
    
	for (i = 0; i < N; i++){
        for(j = 0; j < N; j++){
            for(k = 0; k < N; k++){
#pragma HLS unroll factor=16                
                sum += A[i][k] * B[k][j];
            }
            C[i][j] = sum;
            sum = 0;
        }
    }
}
