public int maximumSum(int[] arr) {
        int noDelete = arr[0];
        int oneDelete = Integer.MIN_VALUE;
        int result = arr[0];
        for(int i=1;i<arr.length;i++)
        {
            int prevNoDelete = noDelete;
            int prevOneDelete = oneDelete;
            int v2;
            if(prevOneDelete == Integer.MIN_VALUE)
            {
                v2 = arr[i];
            }
            else
            {
                v2 = prevOneDelete + arr[i];
            }
            oneDelete = Math.max(v2, prevNoDelete);
            noDelete = Math.max(noDelete + arr[i], arr[i]);
            result = Math.max(result,(Math.max(oneDelete, noDelete)));
        }
        return result;
    }
