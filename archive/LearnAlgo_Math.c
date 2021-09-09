#include <stdint.h>

/*
 * Finds the Greatest Common Divisor for numbers a and b
 * Uses Euclidean Theorem
 */
uint32_t find_gcd(uint32_t a, uint32_t b) {
    // Trivial cases
    if(a == 0) {
        return b;
    }
    if(b == 0) {
        return a;
    }
    if(a == b) {
        return a;
    }

    if(a > b) {
        return find_gcd(b, (a % b));   // Recursive call with new pair (b, a mod b)
    } else {
        return find_gcd(a, (b % a));   // Recursive call with new pair (a, b mod a)
    }
}

/*
 * Source: https://www.interviewcake.com/question/python/stock-price
 * Given an array of per minute stock prices of a stock, find the indices of buy and then sell that'll make the best profit
 * No short selling allowed, and buying is necessary before selling. Note that profit can be negative also!
 */
uint32_t max_profit() {
    uint32_t stock_prices[6*60];    // 6 hours trading day, prices update every minute

    // TODO
}

/*
 * Define Fib(n) as nth Fibonacci number, Fib(0) = 0, Fib(1) = 1 ..., then find Fib(n) mod m
 */
uint32_t fibonacci_mod(uint32_t fib_idx, uint32_t m) {
    // TODO
}

/*
 * Find the sum of unit's place digit for the sum of two Fibonacci numbers, at index i and j; Fib(n) such that Fib(0) = 0, Fib(1) = 1
 */
uint32_t unit_dig_fib_sum(uint32_t i, uint32_t j) {
    // TODO
}

/*
 * Celebration Party: Given a group of children and their age, organize them in minimum no. of groups such that within each group,
 * age of any 2 children differ at most by 2 years
 */
void celebration_party() {
    uint8_t children_age[100];  // ages of children; assume 100 children attend the party;

    // Sort the array in ascending order of age; then traverse the sorted array and partition at boundary where age difference > 2
}

void Insertion_Sort() {
    for(int i = 1; i < n; i++) {
        int h = i;  // Original position of insertion
        int val = arr[h];
        // Only need to check until find arr[h-1] < val
        while(h > 0 && (arr[h-1] > val)) {
            arr[h] = arr[h-1];
            h--;
        }
        arr[h] = val;   // Insert the arr[i] at right place in sorted part
    }
}
