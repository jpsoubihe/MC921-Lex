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
  store i32 3, i32* %"2"
  %"4" = alloca i32
  store i32 6, i32* %"4"
  %"9" = alloca i32
  store i32 1, i32* %"9"
  br label %"6"
"6":
  %".6" = load i32, i32* %"4"
  %".7" = load i32, i32* %"9"
  %".8" = icmp slt i32 %".7", %".6"
  br i1 %".8", label %"7", label %"8"
"7":
  %".10" = load i32, i32* %"4"
  %".11" = load i32, i32* %"2"
  %".12" = icmp sge i32 %".11", %".10"
  br i1 %".12", label %"14", label %"15"
"14":
  br label %"8"
"8":
  %".22" = load i32, i32* %"4"
  %".23" = load i32, i32* %"2"
  %".24" = icmp eq i32 %".23", %".22"
  br i1 %".24", label %"28", label %"29"
"15":
  %".15" = load i32, i32* %"2"
  %".16" = add i32 %".15", 1
  store i32 %".16", i32* %"2"
  %".18" = load i32, i32* %"9"
  %".19" = add i32 %".18", 1
  store i32 %".19", i32* %"9"
  br label %"6"
"28":
  br label %"30"
"30":
  store i32 0, i32* %"0"
  br label %"1"
"29":
  br label %"1"
"1":
  %".30" = load i32, i32* %"0"
  ret i32 %".30"
}
