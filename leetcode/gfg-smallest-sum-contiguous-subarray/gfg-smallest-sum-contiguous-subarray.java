public int minSubarraySum(int[] arr) {
        int best = arr[0];
        int ans = arr[0];
        for(int i=1;i<arr.length;i++)
        {
           int v1 = best+arr[i];
           int v2 = arr[i];
           best = Math.min(v1, v2);
           ans = Math.min(ans,best);
        }
        return ans;
    }
