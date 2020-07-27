; ModuleID = "/home/joao/PycharmProjects/MC921-Lex/CodeGen.py"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...) 

declare i32 @"scanf"(i8* %".1", ...) 

@".str.0" = internal constant [5 x i32] [i32 1, i32 2, i32 3, i32 4, i32 5]
@".str.1" = constant [5 x i8] c"xpto\00"
@".str.2" = constant [15 x i8] c"assertion_fail\00"
define i32 @"main"() 
{
main:
  %"0" = alloca i32
  %"2" = alloca [5 x i32]
  store [5 x i32] [i32 1, i32 2, i32 3, i32 4, i32 5], [5 x i32]* %"2"
  %"3" = alloca [5 x i8]
  store [5 x i8] c"xpto\00", [5 x i8]* %"3"
  %"4" = alloca [5 x i8]
  %"5" = alloca i32
  store i32 2, i32* %"5"
  %"7" = alloca i32
  store i32 3, i32* %"7"
  %"9" = alloca i32
  store i32 4, i32* %"9"
  %".7" = getelementptr [5 x i8], [5 x i8]* %"3", i32 0, i32 1
  %".8" = load i8, i8* %".7"
  %".9" = getelementptr [5 x i8], [5 x i8]* %"4", i32 0, i32 2
  store i8 %".8", i8* %".9"
  %".11" = load i32, i32* %"9"
  %".12" = load i32, i32* %"7"
  %".13" = load i32, i32* %"5"
  %".14" = add i32 %".13", %".12"
  %".15" = add i32 %".14", %".11"
  %".16" = load i32, i32* %"5"
  %".17" = getelementptr [5 x i32], [5 x i32]* %"2", i32 0, i32 2
  store i32 %".15", i32* %".17"
  %".19" = load i32, i32* %"7"
  %".20" = sub i32 %".19", 2
  store i32 %".20", i32* %"7"
  %".22" = load i32, i32* %"5"
  %".23" = getelementptr [5 x i32], [5 x i32]* %"2", i32 0, i32 2
  %".24" = load i32, i32* %".23"
  %".25" = icmp eq i32 %".24", 9
  %".26" = load i32, i32* %"7"
  %".27" = getelementptr [5 x i8], [5 x i8]* %"3", i32 0, i32 %".20"
  %".28" = load i8, i8* %".27"
  %".29" = load i32, i32* %"5"
  %".30" = getelementptr [5 x i8], [5 x i8]* %"4", i32 0, i32 2
  %".31" = load i8, i8* %".30"
  %".32" = icmp eq i8 %".31", %".28"
  %".33" = and i1 %".32", %".25"
  br i1 %".33", label %"39", label %"40"
"39":
  br label %"41"
"41":
  store i32 0, i32* %"0"
  br label %"1"
"40":
  br label %"1"
"1":
  %".39" = load i32, i32* %"0"
  ret i32 %".39"
}
