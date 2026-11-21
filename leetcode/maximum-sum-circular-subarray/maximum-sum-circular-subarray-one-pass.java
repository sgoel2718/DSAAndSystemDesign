public int maxSubarraySumCircular(int[] nums) {
    int total = 0, maxEnd = nums[0], minEnd = nums[0], maxAns = nums[0], minAns = nums[0];
    for (int i = 0; i < nums.length; i++) {
        total += nums[i];
        if (i == 0) continue;
        maxEnd = Math.max(maxEnd + nums[i], nums[i]);  maxAns = Math.max(maxAns, maxEnd);
        minEnd = Math.min(minEnd + nums[i], nums[i]);  minAns = Math.min(minAns, minEnd);
    }
    return maxAns < 0 ? maxAns : Math.max(maxAns, total - minAns);
}
