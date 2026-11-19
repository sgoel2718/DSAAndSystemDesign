int countTriplets(int sum, int arr[]) {
       Arrays.sort(arr);
       int count = 0;
       for (int i = 0; i < arr.length - 2; i++) {
           int l = i + 1, r = arr.length - 1;
           while (l < r) {
               if (arr[i] + arr[l] + arr[r] < sum) {
                   count += r - l;
                   l++;
               } else r--;
           }
       }
       return count;
    }
