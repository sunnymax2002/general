int* Merge(int* L, int sL, int* R, int sR) {
    int iL = 0;
    int iR = 0;
    int* iP = L;    // Initial insertion pointer is start of L
    int ioff = 0;   // Offset from iP for insertion
    while(iL < sL || iR < sR) {
        int vL = *(L + iL);
        int vR = *(R + iR);
        if(vL <= vR) {
            *(iP + ioff) = vL;
            iL++;
        } else {
            *(iP + ioff) = vR;
            iR++;
        }
        ioff++;
        // insertion in L finished, 
        if(ioff == sL) {
            iP = R;
            ioff = 0;
        }
    }
}

int* MergeSort(int* arr, int n) {
    if(n < 2) {
        return arr;
    }

    int mid = (int)(n/2);
    int sL = mid;
    int sR = n - mid;
    int* L = MergeSort(arr, sL);
    int* R = MergeSort(arr + mid, sR);

    return Merge(L, sL, R, sR);
}