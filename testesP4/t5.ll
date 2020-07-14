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
  store i32 1, i32* %"2"
  %"4" = alloca i32
  store i32 0, i32* %"4"
  %"6" = alloca i32
  %".4" = load i32, i32* %"2"
  %".5" = add i32 %".4", 17327
  store i32 %".5", i32* %"2"
  br label %"10"
"10":
  %".8" = load i32, i32* %"2"
  %".9" = icmp sgt i32 %".8", 0
  br i1 %".9", label %"11", label %"12"
"11":
  %".11" = load i32, i32* %"2"
  %".12" = srem i32 %".11", 10
  store i32 %".12", i32* %"6"
  %".14" = load i32, i32* %"6"
  %".15" = load i32, i32* %"4"
  %".16" = mul i32 %".15", 10
  %".17" = add i32 %".16", %".14"
  store i32 %".17", i32* %"4"
  %".19" = load i32, i32* %"2"
  %".20" = sdiv i32 %".19", 10
  store i32 %".20", i32* %"2"
  br label %"10"
"12":
  %".23" = load i32, i32* %"4"
  %".24" = icmp eq i32 %".23", 82371
  br i1 %".24", label %"30", label %"31"
"30":
  br label %"32"
"32":
  store i32 0, i32* %"0"
  br label %"1"
"31":
  br label %"1"
"1":
  %".30" = load i32, i32* %"0"
  ret i32 %".30"
}
