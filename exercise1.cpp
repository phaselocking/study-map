#include <iostream>
using namespace std;


struct SqList {
    int data[100];
    int length;
};

void intervalDelete(SqList &L, int k1, int k2){
    //查找k1到k2区间
    int i = -1;
    int j = -1;
    for(int m = 0; m < L.length; m++){
        if(i < 0 && L.data[m] > k1)
            i = m;
        if(j < 0 && L.data[m] >= k2){
            j = m;
            break;
        }
    }
    if(i < 0){
        cout << "Interval Not Found";
        return;
    }
    if(i != -1 && j == -1)
        j = L.length; 
    //开始覆盖
    while(j < L.length){
        L.data[i] = L.data[j];
        i++;
        j++;
    }
    //修改顺序表逻辑长度
    L.length = i;
}


int main() {
    SqList L = {{1, 2, 3, 4, 5}, 5};

    intervalDelete(L, 2, 4);

    for (int i = 0; i < L.length; i++)
        cout << L.data[i] << " ";
}


//21:43 261022 hard but...