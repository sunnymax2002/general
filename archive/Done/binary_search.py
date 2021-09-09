# Given an input array of size n (indexed from 0 to n-1), which is sorted in ascending order,
# but rotated such that at an unknown index 't', 0 < t < n-1, v[t] is minimum, instead of v[0]
# Example: [3,4,6,8,10,24,45,-5,-2,-1,0,1,2]
# Goal: Find an element in this array

arry = [3,4,6,8,10,24,45,-5,-2,-1,0,1,2]        # input array
x = 3      # value to search

left = 0
right = len(arry) - 1

x_idx = -1

iter_cnt = 0

while(right >= left):
    iter_cnt += 1       # keep track of iterations

    mid = left + int((right - left) / 2)
    vmid = arry[mid]
    vleft = arry[left]

    if(x == vmid):
        x_idx = mid
        break
    if(x == vleft):
        x_idx = left
        break

    if(x > vmid):
        # in right half
        left = mid + 1
    else:
        if(x < vleft):
            # in right half
            left = mid + 1
        else:
            right = mid + 1

if(x_idx == -1):
    print("Error")