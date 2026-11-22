public int numSubarrayProductLessThanK(int[] nums, int k) {
        if(k<=1) return 0;
        long prod = 1;
        int l=0, count = 0;
        for(int r=0;r<nums.length;r++)
        {
            prod*=nums[r];
            while(prod>=k) prod/=nums[l++];
            count += r-l+1;
        }
        return count;
    }
