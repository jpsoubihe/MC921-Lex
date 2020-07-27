int d;

int foo(int a, int b, int c) {
  int x, y, z;
  z = a + b + c;
  a = b + c;
  x = a;
  y = x;
  return x + 2*y + c;
}

int main() {
  int a = 1, b = 2, c = 3;
  d = foo(a, b, c);
  assert d == c * c * b;
  return 0;
}