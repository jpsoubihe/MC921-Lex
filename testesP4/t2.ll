; ModuleID = "/home/joao/PycharmProjects/MC921-Lex/CodeGen.py"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...) 

declare i32 @"scanf"(i8* %".1", ...) 

@".str.0" = constant [15 x i8] c"assertion_fail\00"
define i32 @"f"(i32 %"0", i32 %"1") 
{
f:
  %"2" = alloca i32
  %"3" = alloca i32
  %"4" = alloca i32
  store i32 %"0", i32* %"3"
  store i32 %"1", i32* %"4"
  %"6" = alloca i32
  %"7" = alloca i32
  %"8" = alloca i32
  %".6" = load i32, i32* %"3"
  %".7" = icmp slt i32 %".6", 2
  br i1 %".7", label %"9", label %"10"
"9":
  store i32 0, i32* %"4"
  store i32 %"0", i32* %"2"
  br label %"5"
"5":
  %".29" = load i32, i32* %"2"
  ret i32 %".29"
"10":
  %".12" = load i32, i32* %"3"
  %".13" = sub i32 %".12", 2
  %".14" = load i32, i32* %"7"
  %".15" = call i32 @"f"(i32 %".13", i32 %".14")
  %".16" = load i32, i32* %"3"
  %".17" = sub i32 %".16", 1
  %".18" = load i32, i32* %"6"
  %".19" = call i32 @"f"(i32 %".17", i32 %".18")
  %".20" = add i32 %".19", %".15"
  store i32 %".20", i32* %"8"
  %".22" = load i32, i32* %"7"
  %".23" = load i32, i32* %"6"
  %".24" = add i32 %".23", %".22"
  %".25" = add i32 %".24", 1
  store i32 %".25", i32* %"4"
  store i32 %".20", i32* %"2"
  br label %"5"
}

define i32 @"main"() 
{
main:
  %"0" = alloca i32
  %"2" = alloca i32
  store i32 9, i32* %"2"
  %".3" = load i32, i32* %"2"
  %".4" = load i32, i32* %"2"
  %".5" = add i32 %".4", %".3"
  %".6" = load i32, i32* %"2"
  %".7" = load i32, i32* %"2"
  %".8" = call i32 @"f"(i32 3, i32 %".7")
  %".9" = mul i32 %".8", %".6"
  %".10" = icmp eq i32 %".9", %".5"
  br i1 %".10", label %"13", label %"14"
"13":
  br label %"15"
"15":
  store i32 0, i32* %"0"
  br label %"1"
"14":
  br label %"1"
"1":
  %".16" = load i32, i32* %"0"
  ret i32 %".16"
}
