; ModuleID = "/home/joao/PycharmProjects/MC921-Lex/CodeGen.py"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...) 

declare i32 @"scanf"(i8* %".1", ...) 

@"n" = internal constant i32 10
@".str.0" = constant [15 x i8] c"assertion_fail\00"
define i32 @"foo"(i32 %"0", i32 %"1") 
{
foo:
  %"2" = alloca i32
  %"3" = alloca i32
  %"4" = alloca i32
  store i32 %"0", i32* %"3"
  store i32 %"1", i32* %"4"
  %".6" = load i32, i32* %"4"
  %".7" = load i32, i32* %"3"
  %".8" = add i32 %".7", %".6"
  %".9" = load i32, i32* @"n"
  %".10" = mul i32 %".9", %".8"
  store i32 %".10", i32* %"2"
  br label %"5"
"5":
  %".13" = load i32, i32* %"2"
  ret i32 %".13"
}

define i32 @"main"() 
{
main:
  %"0" = alloca i32
  %"2" = alloca i32
  store i32 2, i32* %"2"
  %"4" = alloca i32
  store i32 3, i32* %"4"
  %"6" = alloca i32
  %".4" = load i32, i32* %"2"
  %".5" = load i32, i32* %"4"
  %".6" = call i32 @"foo"(i32 %".4", i32 %".5")
  store i32 10, i32* %"6"
  %".8" = load i32, i32* %"6"
  %".9" = icmp eq i32 %".8", 50
  br i1 %".9", label %"13", label %"14"
"13":
  br label %"15"
"15":
  store i32 0, i32* %"0"
  br label %"1"
"14":
  br label %"1"
"1":
  %".15" = load i32, i32* %"0"
  ret i32 %".15"
}
