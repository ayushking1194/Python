def rev(a,n=0):
    if a==0:
        return n
    else:
        n=(n*10)+int(a%10)
        return rev(a//10,n)

def pal_check(num,rev):
    if num^rev==0:
        return True
    else:
        return False
a=int(input())
n=rev(a)
print(pal_check(a,n))