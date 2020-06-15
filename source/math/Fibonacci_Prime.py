# Study of Fibonacci sequence and relationship to prime numbers

# https://math.stackexchange.com/questions/913287/relationship-between-primes-and-fibonacci-sequence
# https://en.wikipedia.org/wiki/Fibonacci_prime
# https://en.wikipedia.org/wiki/Lucas_number#:~:text=The%20Lucas%20numbers%20or%20Lucas,complementary%20instances%20of%20Lucas%20sequences.

import math

# Function for nth fibonacci number - Dynamic Programing: https://www.geeksforgeeks.org/python-program-for-program-for-fibonacci-numbers-2/
# Taking 1st two fibonacci nubers as 0 and 1 
FibArray = [0,1] 
# initial prime number list
prime_list = [2]

def fibonacci(n): 
	if n<0: 
		print("Incorrect input") 
	elif n<=len(FibArray): 
		return FibArray[n-1] 
	else: 
		temp_fib = fibonacci(n-1)+fibonacci(n-2) 
		FibArray.append(temp_fib) 
		return temp_fib

# https://codereview.stackexchange.com/questions/158925/generate-nth-prime-number-in-python
def nth_prime_number(n):
    # first number to test if prime
    num = 3
    # keep generating primes until we get to the nth one
    while len(prime_list) < n:

        # check if num is divisible by any prime before it
        for p in prime_list:
            # if there is no remainder dividing the number
            # then the number is not a prime
            if num % p == 0:
                # break to stop testing more numbers, we know it's not a prime
                break

        # if it is a prime, then add it to the list
        # after a for loop, else runs if the "break" command has not been given
        else:
            # append to prime list
            prime_list.append(num)

        # same optimization you had, don't check even numbers
        num += 2

    # return the last prime number generated
    return prime_list[-1]

# https://stackoverflow.com/questions/15347174/python-finding-prime-factors
def prime_factors(n):
    i = 2
    factors = []
    while i * i <= n:
        if n % i:
            i += 1
        else:
            n //= i
            factors.append(i)
    if n > 1:
        factors.append(n)
    return factors

seq_m1 = []
seq_p1 = []
for n in range(1,25):
    seq_m1.append(math.gcd(n, fibonacci(n - 1)))
    seq_p1.append(math.gcd(n, fibonacci(n + 1)))

print(seq_m1)
print(seq_p1)

nth_prime_number(20)
fibonacci(20)
print(prime_list)
print(FibArray)

i = 1
for p in prime_list:
    fib_prime_n_m1 = fibonacci(p - 1)
    fib_prime_n_p1 = fibonacci(p + 1)
    # gcd1 = math.gcd(fib_prime_n_m1, p)
    # gcd2 = math.gcd(fib_prime_n_p1, p)
    # print("GCD1, GCD2 = ", gcd1, gcd2)
    print("Prime(" + str(i) + ") = ", p)
    i += 1
    print("Prime factors of Fib(" + str(p) + " - 1) = " + str(fib_prime_n_m1) + " are: " + str(prime_factors(fib_prime_n_m1)))
    print("Prime factors of Fib(" + str(p) + " + 1) = " + str(fib_prime_n_p1) + " are: " + str(prime_factors(fib_prime_n_p1)))
    print("")

i = 1
for f in FibArray:
    print("Prime factors of " + str(i) + "th Fib-number " + str(f) + " are: " + str(prime_factors(f)))
    i += 1

for n in range(1, 10):
    # fib_n = fibonacci(n)
    prime_n = nth_prime_number(n)
    # print("Fib(" + str(n) + ") = " + str(fib_n))
    print("Prime(" + str(n) + ") = " + str(prime_n))
    fib_prime_n_m1 = fibonacci(prime_n - 1)
    fib_prime_n_p1 = fibonacci(prime_n + 1)
    print("Fib(" + str(prime_n - 1) + ") = " + str(fib_prime_n_m1))
    print("Fib(" + str(prime_n + 1) + ") = " + str(fib_prime_n_p1))
    print(str(fib_prime_n_m1) + " % " + str(prime_n) + " = " + str(fib_prime_n_m1 % prime_n))
    print(str(fib_prime_n_p1) + " % " + str(prime_n) + " = " + str(fib_prime_n_p1 % prime_n))
    print("")