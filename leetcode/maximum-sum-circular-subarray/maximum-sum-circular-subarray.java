public int maxSubarraySumCircular(int[] nums) {
        int total = 0;
        for (int x : nums) total += x;

        int maxKadane = maxSubArray(nums);       
        int minKadane = minSubarraySum(nums);  

        if (maxKadane < 0) return maxKadane;    
        return Math.max(maxKadane, total - minKadane);
    }

    private int maxSubArray(int[] nums) {
        int best = nums[0];
        int ans = nums[0];
        for(int i=1;i<nums.length;i++)
        {
            int v1 = best+nums[i];
            int v2 = nums[i];
            best = Math.max(v1, v2);
            ans = Math.max(ans,best);
        }
        return ans;
    }

    private int minSubarraySum(int[] arr) {
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
