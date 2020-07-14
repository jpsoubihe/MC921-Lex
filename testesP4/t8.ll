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
  store i32 2, i32* %"2"
  %"4" = alloca i32
  %"5" = alloca i32
  %".3" = load i32, i32* %"2"
  %".4" = add i32 %".3", 1
  store i32 %".4", i32* %"2"
  store i32 %".4", i32* %"4"
  %".7" = load i32, i32* %"2"
  %".8" = add i32 %".7", 1
  store i32 %".8", i32* %"2"
  store i32 %".4", i32* %"5"
  %".11" = load i32, i32* %"5"
  %".12" = icmp eq i32 %".11", 3
  %".13" = load i32, i32* %"4"
  %".14" = icmp eq i32 %".13", 3
  %".15" = and i1 %".14", %".12"
  br i1 %".15", label %"19", label %"20"
"19":
  br label %"21"
"21":
  store i32 0, i32* %"0"
  br label %"1"
"20":
  br label %"1"
"1":
  %".21" = load i32, i32* %"0"
  ret i32 %".21"
}
