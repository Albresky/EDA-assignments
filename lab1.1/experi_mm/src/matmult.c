#include <stdio.h>
#include <unistd.h>
#include <math.h>

#include "matmult.h"


//////////////// Original Code ////////////////
/* void matmult(short A[N][N], short B[N][N], short C[N][N]){
	short i, j, k;
    short sum = 0;
    
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
/* void matmult(short A[N][N], short B[N][N], short C[N][N]){
	short i, j, k;
    short sum = 0;
    
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
} */


//////////////// [Op2: Use patition pragma to initialize array into registers] ////////////////
/* void matmult(short A[N][N], short B[N][N], short C[N][N]){
#pragma HLS array_partition variable=A type=complete dim=0
#pragma HLS array_partition variable=B type=complete dim=0
#pragma HLS array_partition variable=C type=complete dim=0
	short i, j, k;
    short sum = 0;
    
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
} */

//////////////// [Op3: Use partition and dataflow pragma to minimize task workload and enable parallelism in task level] ////////////////
#define BLOCK_DIM_A 4
#define BLOCK_DIM_B 4
#define BLOCK_DIM_C 4

void blockMM(short bA[N][N], short bB[N][N], short bC[N][N], short blk_id)
{
#pragma HLS inline off
    short i, j, k;
    short sum=0, blk_dim=N/BLOCK_DIM_B;
    for(i = 0; i < N; i++)
    {
        for(j = 0; j < N; j++)
        {
BLOCK_MM_INNER_LOOP:
            sum = 0;
            for(k = 0; k < blk_dim; k++)
            {
#pragma HLS unroll factor=4
                short blk_elem_idx = k+blk_dim*blk_id;
                sum += bA[i][blk_elem_idx] * bB[blk_elem_idx][j];
            }
            bC[i][j] = sum;
        }
    }
}

void blockMerge(short bA[N][N], short bB[N][N], short bC[N][N])
{
#pragma HLS inline off
    short i, j, k;
    for(i = 0; i < N; i++)
    {
BLOCK_MERGE_INNER_LOOP:
        for(j = 0; j < N; j++)
        {
#pragma HLS pipeline II=1            
            bC[i][j] = bA[i][j] + bB[i][j];
        }
    }
}

void wrapperMM(short A[N][N], short B[N][N], short tempC[BLOCK_DIM_C][N][N])
{
#pragma HLS dataflow
    blockMM(A,B,tempC[0], 0);
    blockMM(A,B,tempC[1], 1);
    blockMM(A,B,tempC[2], 2);
    blockMM(A,B,tempC[3], 3);
}

void wrapperMG(short tempC[BLOCK_DIM_A+2][N][N])
{
#pragma HLS dataflow
    blockMerge(tempC[0], tempC[1], tempC[4]);
    blockMerge(tempC[2], tempC[3], tempC[5]);
}

void printMat(short mat[N][N])
{
    for(short i=0;i<N;i++)
    {
        for(short j=0;j<N;j++)
        {
            printf("%d\t", mat[i][j]);
        }
        printf("\n");
    }
}

void matmult(short A[N][N], short B[N][N], short C[N][N])
{
#pragma HLS array_partition variable=A type=block factor=4 dim=2
#pragma HLS array_partition variable=B type=block factor=4 dim=1

    short tempC[BLOCK_DIM_C+2][N][N];
#pragma HLS bind_storage variable=tempC type=RAM_T2P impl=BRAM
#pragma HLS array_partition variable=tempC type=complete dim=1

    wrapperMM(A, B, tempC);

/*     printf("tempC[0]:\n");
    printMat(tempC[0]);
    printf("tempC[1]:\n");
    printMat(tempC[1]);
    printf("tempC[2]:\n");
    printMat(tempC[2]);
    printf("tempC[3]:\n");
    printMat(tempC[3]); */

    wrapperMG(tempC);

    blockMerge(tempC[4], tempC[5], C);
}

