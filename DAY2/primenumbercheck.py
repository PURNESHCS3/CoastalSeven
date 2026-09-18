num=int(input())
val=0
if num>=0:
    print("NOT SUITABLE FOR CHECK")
for i in range(2,(num//2)+1):
    if num%i==0:
        val+=1
if val>=1:
    print("NOT A PRIME")
elif val==0:
    print("PRIME")