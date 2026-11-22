public int minSubArrayLen(int target, int[] nums) {
        int l = 0, sum = 0, best = Integer.MAX_VALUE;
        for(int r=0;r<nums.length;r++)
        {
            sum+=nums[r];
            while(sum>=target)
            {
                best = Math.min(best, r-l+1);
                sum-=nums[l];
                l++;
            }
        }
        return best == Integer.MAX_VALUE ? 0 : best;
    }
