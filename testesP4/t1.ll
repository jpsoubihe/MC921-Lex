; ModuleID = "/home/joao/PycharmProjects/MC921-Lex/CodeGen.py"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...) 

declare i32 @"scanf"(i8* %".1", ...) 

@"v" = internal constant [4 x i32] [i32 1, i32 2, i32 3, i32 4]
@".str.1" = constant [15 x i8] c"assertion_fail\00"
define void @"main"() 
{
main:
  %"2" = alloca i32
  store i32 0, i32* %"2"
  %"7" = alloca i32
  store i32 0, i32* %"7"
  br label %"4"
"4":
  %".5" = load i32, i32* %"7"
  %".6" = icmp slt i32 %".5", 4
  br i1 %".6", label %"5", label %"6"
"5":
  %".8" = load i32, i32* %"7"
  %".9" = getelementptr [4 x i32], [4 x i32]* @"v", i32 0, i32 0
  %".10" = load i32, i32* %".9"
  %".11" = load i32, i32* %"2"
  %".12" = add i32 %".11", %".10"
  store i32 %".12", i32* %"2"
  %".14" = load i32, i32* %"7"
  %".15" = add i32 %".14", 1
  store i32 %".15", i32* %"7"
  br label %"4"
"6":
  %".18" = load i32, i32* %"2"
  %".19" = icmp eq i32 %".18", 10
  br i1 %".19", label %"23", label %"24"
"23":
  br label %"25"
"25":
  br label %"1"
"24":
  br label %"1"
"1":
  ret void
}
