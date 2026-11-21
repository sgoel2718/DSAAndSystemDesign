public int maxAbsoluteSum(int[] nums) {
        int sum = 0, hi = 0, lo = 0;
        for (int x : nums) 
        {
             sum += x; 
             hi = Math.max(hi, sum); 
             lo = Math.min(lo, sum);
        }
        return hi - lo;
    }
