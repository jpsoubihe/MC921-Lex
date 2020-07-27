int z, t;

int foo (int t) {
  int x;
  t = t * 2;
  x = 2 * t;
  z = x + 1;
  return x;
}

int main() {
  int y;
  z = 3;
  t = 4;
  y = foo(t + z);
  assert z == y + 1;
  return 0;
}
