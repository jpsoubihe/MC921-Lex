int main() {
  int a = 1, b = 2, c = 3, d = 4, e = 5;
  b = a;
  c = 4 * b;
  if (c > b)
    d = b + 2;
  e = a + b;
  assert d == e + b;
  return 0;
}

