int f(int n, int k) {
    int p, q, t;
    if (n < 2) {
        k = 0;
        return n;
    }
    else {
        t = f(n-1, p) + f(n-2, q);
        k = p + q + 1;
        int n = 4;
        return t;
    }
}

void main() {
    int m = 9;
    int n = 3;
    print(f(3, m), m);
}