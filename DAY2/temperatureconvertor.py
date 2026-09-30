n=int(input("1- C TO F \n2- F TO C \n"))
if n==1:
    c=int(input("ENTER TEMPERATURE IN CELSIUS: "))
    print("TEMPERATURE IN FAHRENHEIT",((c*9/5)+32),"F")
elif n==2:
    f=float(input("ENTER TEMPERATURE IN FAHRENHEIT: "))
    print("TEMPERATURE IN CELSIUS",int(((f-32)*5)/9),"C")
else:
    print("ENTER VALID OPTION")