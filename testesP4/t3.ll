; ModuleID = "/home/joao/PycharmProjects/MC921-Lex/CodeGen.py"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...) 

declare i32 @"scanf"(i8* %".1", ...) 

@".str.0" = constant [15 x i8] c"assertion_fail\00"
define i32 @"main"() 
{
main:
  %"0" = alloca i32
  %"2" = alloca i32
  %"3" = alloca i32
  %"4" = alloca i32
  %"5" = alloca double
  store double              0x0, double* %"5"
  store i32 5743475, i32* %"2"
  %".4" = load i32, i32* %"2"
  store i32 5743475, i32* %"4"
  br label %"9"
"9":
  %".7" = load i32, i32* %"2"
  %".8" = icmp sgt i32 %".7", 0
  br i1 %".8", label %"10", label %"11"
"10":
  %".10" = load i32, i32* %"2"
  %".11" = srem i32 %".10", 10
  store i32 %".11", i32* %"3"
  %".13" = load i32, i32* %"3"
  %".14" = sitofp i32 %".13" to double
  %".15" = load double, double* %"5"
  %".16" = fmul double %".15", 0x4024000000000000
  %".17" = fadd double %".16", %".14"
  store double %".17", double* %"5"
  %".19" = load i32, i32* %"2"
  %".20" = sdiv i32 %".19", 10
  store i32 %".20", i32* %"2"
  br label %"9"
"11":
  %".23" = load double, double* %"5"
  %".24" = fptosi double %".23" to i32
  %".25" = load i32, i32* %"4"
  %".26" = icmp eq i32 %".25", %".24"
  br i1 %".26", label %"31", label %"32"
"31":
  br label %"33"
"33":
  store i32 0, i32* %"0"
  br label %"1"
"32":
  br label %"1"
"1":
  %".32" = load i32, i32* %"0"
  ret i32 %".32"
}
