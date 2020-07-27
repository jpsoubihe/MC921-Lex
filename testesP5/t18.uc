int main() {
  int a = 5, b = 2, c, d, e, f = 3, g, h = 1;
  c = a + b;
  d = c;
  e = d * d;
  while (h < f) {
    f = a + c;
    g = e;
    a = g + d;
    if (a < c)
      h = g + 1;
    else {
      f = d - g;
    }
    b = g * a;
  }
  assert b == 2744;
  return 0;
}
