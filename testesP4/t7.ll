; ModuleID = "/home/joao/PycharmProjects/MC921-Lex/CodeGen.py"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...) 

declare i32 @"scanf"(i8* %".1", ...) 

@".str.0" = constant [15 x i8] c"assertion_fail\00"
define i32 @"gcd"(i32 %"0", i32 %"1") 
{
gcd:
  %"2" = alloca i32
  %"3" = alloca i32
  %"4" = alloca i32
  store i32 %"0", i32* %"3"
  store i32 %"1", i32* %"4"
  %"6" = alloca i32
  %".6" = load i32, i32* %"4"
  store i32 %"1", i32* %"6"
  br label %"8"
"8":
  %".9" = load i32, i32* %"3"
  %".10" = icmp sgt i32 %".9", 0
  br i1 %".10", label %"9", label %"10"
"9":
  %".12" = load i32, i32* %"3"
  store i32 %"0", i32* %"6"
  %".14" = load i32, i32* %"3"
  %".15" = load i32, i32* %"3"
  %".16" = load i32, i32* %"4"
  %".17" = sdiv i32 %".16", %".15"
  %".18" = mul i32 %".17", %".14"
  %".19" = load i32, i32* %"4"
  %".20" = sub i32 %".19", %".18"
  store i32 %".20", i32* %"3"
  %".22" = load i32, i32* %"6"
  store i32 %"0", i32* %"4"
  br label %"8"
"10":
  store i32 %"0", i32* %"2"
  br label %"5"
"5":
  %".27" = load i32, i32* %"2"
  ret i32 %".27"
}

define void @"main"() 
{
main:
  %"2" = alloca i32
  store i32 198, i32* %"2"
  %"4" = alloca i32
  store i32 36, i32* %"4"
  %".4" = load i32, i32* %"2"
  %".5" = load i32, i32* %"4"
  %".6" = call i32 @"gcd"(i32 %".4", i32 %".5")
  %".7" = icmp eq i32 %".6", 18
  br i1 %".7", label %"11", label %"12"
"11":
  br label %"13"
"13":
  br label %"1"
"12":
  br label %"1"
"1":
  ret void
}
