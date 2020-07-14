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
  store i32 11, i32* %"2"
  store i32 99, i32* %"3"
  %".4" = load i32, i32* %"3"
  %".5" = load i32, i32* %"2"
  %".6" = add i32 %".5", %".4"
  store i32 %".6", i32* %"2"
  %".8" = load i32, i32* %"3"
  %".9" = load i32, i32* %"2"
  %".10" = sub i32 %".9", %".8"
  store i32 %".10", i32* %"3"
  %".12" = load i32, i32* %"3"
  %".13" = load i32, i32* %"2"
  %".14" = sub i32 %".13", %".12"
  store i32 %".14", i32* %"2"
  %".16" = load i32, i32* %"3"
  %".17" = icmp eq i32 %".16", 11
  %".18" = load i32, i32* %"2"
  %".19" = icmp eq i32 %".18", 99
  %".20" = and i1 %".19", %".17"
  br i1 %".20", label %"22", label %"23"
"22":
  br label %"24"
"24":
  store i32 0, i32* %"0"
  br label %"1"
"23":
  br label %"1"
"1":
  %".26" = load i32, i32* %"0"
  ret i32 %".26"
}
