#include <stdio.h>

int v[2] = {1.2, 2, 3};
int main() {
	int g = 4;
	char c = 'j';
	char d = 'f';

	printf("---------------- BINARY CHAR-CHAR OPERATIONS ----------------\n");	
	printf("TIMES = %c\n", c*d);
	printf("DIVIDE = %c\n", c/d);
	printf("MOD = %c\n", c%d);
	printf("PLUS = %c\n", c+d);
	printf("MINUS = %c\n", c-d);
	printf("LESS_THAN = %c\n", c<d);
	printf("LESS_OR_EQUAL = %c\n", c<=d);
	printf("HIGHER_THAN = %c\n", c>d);
	printf("HIGHER_OR_EQUAL = %c\n", c>=d);
	printf("EQ = %c\n", c == d);
	printf("DIFF = %c\n", c != d);
	printf("AND = %c\n", c && d);
	printf("OR = %c\n", c || d);
	printf("---------------- ASSIGN CHAR-CHAR OPERATIONS ----------------\n");
//	printf("EQUALS = %c\n", c = d); 
//	printf("TIMESASSIGN = %c\n", c *= d);
//	printf("DIVIDEASSIGN = %c\n", c /= d);
//	printf("MODASSIGN = %c\n", c %= d);
//	printf("PLUSASSIGN = %c\n", c += d);
//	printf("MINUSASSIGN = %c\n", c -= d);
	printf("---------------- UNARY CHAR OPERATIONS ----------------\n");
	printf("PLUSPLUS = %c\n", c++);
	printf("MINUSMINUS = %c\n", c--);
	printf("PLUSPLUS = %c\n", ++c);
	printf("MINUSMINUS = %c\n", --c);


	printf("---------------- BINARY INT-INT OPERATIONS ----------------\n");
	int a = 2;
	int b = 3;	
	printf("TIMES = %d\n", a * b);
	printf("DIVIDE = %d\n", a / b);
	printf("MOD = %d\n", a % b);
	printf("PLUS = %d\n", a + b);
	printf("MINUS = %d\n", a - b);
	printf("LESS_THAN = %d\n", a < b);
	printf("LESS_OR_EQUAL = %d\n", a <= b);
	printf("HIGHER_THAN = %d\n", a > b);
	printf("HIGHER_OR_EQUAL = %d\n", a >= b);
	printf("EQ = %d\n", a == b);
	printf("DIFF = %d\n", a != b);
	printf("AND = %d\n", a && b);
	printf("OR = %d\n", a || b);
	printf("---------------- ASSIGN INT-INT OPERATIONS ----------------\n");
	printf("EQUALS = %d\n", a = b);
	printf("TIMESASSIGN = %d\n", a *= b);
	printf("DIVIDEASSIGN = %d\n", a /= b);
	printf("MODASSIGN = %d\n", a %= b);
	printf("PLUSASSIGN = %d\n", a += b);
	printf("MINUSASSIGN = %d\n", a -= b);
	printf("---------------- UNARY INT OPERATIONS ----------------\n");
	printf("PLUSPLUS = %d\n", a++);
	printf("MINUSMINUS = %d\n", a--);
	printf("PLUSPLUS = %d\n", ++a);
	printf("MINUSMINUS = %d\n", --a);


	printf("---------------- BINARY FLOAT-FLOAT OPERATIONS ----------------\n");
	float e = 2.03;
	float f = 3.2;	
	printf("TIMES = %f\n", e * f);
	printf("DIVIDE = %f\n", e / f);
//	printf("MOD = %f\n", e % f); -------- INVALID
	printf("PLUS = %f\n", e + f);
	printf("MINUS = %f\n", e - f);
	printf("LESS_THAN = %f\n", e < f);
	printf("LESS_OR_EQUAL = %f\n", e <= f);
	printf("HIGHER_THAN = %f\n", e > f);
	printf("HIGHER_OR_EQUAL = %f\n", e >= f);
	printf("EQ = %f\n", e == f);
	printf("DIFF = %f\n", e != f);
	printf("AND = %f\n", e && f);
	printf("OR = %f\n", e || f);
	printf("---------------- ASSIGN FLOAT-FLOAT OPERATIONS ----------------\n");
	printf("EQUALS = %f\n", e = f);
	printf("TIMESASSIGN = %f\n", e *= f);
	printf("DIVIDEASSIGN = %f\n", e /= f);
//	printf("MODASSIGN = %f\n", e %= f); -------- INVALID
	printf("PLUSASSIGN = %f\n", e += f);
	printf("MINUSASSIGN = %f\n", e -= f);
	printf("---------------- UNARY FLOAT OPERATIONS ----------------\n");
	printf("PLUSPLUS = %f\n", e++);
	printf("MINUSMINUS = %f\n", e--);
	printf("PLUSPLUS = %f\n", ++e);
	printf("MINUSMINUS = %f\n", --e);


	printf("---------------- BINARY INT-FLOAT OPERATIONS ----------------\n");
	int aux1 = a * e;
	float aux2 = a * e;	
	printf("TIMES = %d\n", a * e);
	printf("DIVIDE = %d\n", a / e);
//	printf("MOD = %d\n", a % e); -------- INVALID
	printf("PLUS = %d\n", a + e);
	printf("MINUS = %d\n", a - e);
	printf("LESS_THAN = %d\n", a < e);
	printf("LESS_OR_EQUAL = %d\n", a <= e);
	printf("HIGHER_THAN = %d\n", a > e);
	printf("HIGHER_OR_EQUAL = %d\n", a >= e);
	printf("EQ = %d\n", a == e);
	printf("DIFF = %d\n", a != e);
	printf("AND = %d\n", a && e);
	printf("OR = %d\n", a || e);
	printf("---------------- ASSIGN INT-FLOAT OPERATIONS ----------------\n");
	printf("EQUALS = %f\n", a = f);
	printf("TIMESASSIGN = %f\n", a *= f);
	printf("DIVIDEASSIGN = %f\n", a /= f);
//	printf("MODASSIGN = %f\n", a %= f); -------- INVALID
	printf("PLUSASSIGN = %f\n", a += f);
	printf("MINUSASSIGN = %f\n", a -= f);

	printf("---------------- BINARY INT-CHAR OPERATIONS ----------------\n");
	printf("TIMES = %d\n", a * c);
	printf("DIVIDE = %d\n", a / c);
	printf("MOD = %d\n", a % c);
	printf("PLUS = %d\n", a + c);
	printf("MINUS = %d\n", a - c);
	printf("LESS_THAN = %d\n", a < c);
	printf("LESS_OR_EQUAL = %d\n", a <= c);
	printf("HIGHER_THAN = %d\n", a > c);
	printf("HIGHER_OR_EQUAL = %d\n", a >= c);
	printf("EQ = %d\n", a == c);
	printf("DIFF = %d\n", a != c);
	printf("AND = %d\n", a && c);
	printf("OR = %d\n", a || c);
	printf("---------------- ASSIGN INT-CHAR OPERATIONS ----------------\n");
	printf("EQUALS = %d\n", a = c);
	printf("TIMESASSIGN = %d\n", a *= c);
	printf("DIVIDEASSIGN = %d\n", a /= c);
	printf("MODASSIGN = %d\n", a %= c); 
	printf("PLUSASSIGN = %d\n", a += c);
	printf("MINUSASSIGN = %d\n", a -= c);


	printf("---------------- BINARY FLOAT-CHAR OPERATIONS ----------------\n");
	printf("TIMES = %f\n", e * c);
	printf("DIVIDE = %f\n", e / c);
//	printf("MOD = %f\n", e % c); -------- INVALID
	printf("PLUS = %f\n", e + c);
	printf("MINUS = %f\n", e - c);
	printf("LESS_THAN = %f\n", e < c);
	printf("LESS_OR_EQUAL = %f\n", e <= c);
	printf("HIGHER_THAN = %f\n", e > c);
	printf("HIGHER_OR_EQUAL = %f\n", e >= c);
	printf("EQ = %f\n", e == c);
	printf("DIFF = %f\n", e != c);
	printf("AND = %f\n", e && c);
	printf("OR = %f\n", e || c);
	printf("---------------- ASSIGN FLOAT-CHAR OPERATIONS ----------------\n");
	printf("EQUALS = %f\n", e = c);
	printf("TIMESASSIGN = %f\n", e *= c);
	printf("DIVIDEASSIGN = %f\n", e /= c);
//	printf("MODASSIGN = %f\n", e %= c); -------- INVALID
	printf("PLUSASSIGN = %f\n", e += c);
	printf("MINUSASSIGN = %f\n", e -= c);



	return 0;
}

