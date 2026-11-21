void segregate0and1(int[] arr) {
        // code here
        int low = 0;
        int high = arr.length-1;
        while(low<high)
        {
            if(arr[low] == 0)   low++;
            else if(arr[high] == 1) high--;
            else
            {
                arr[low]=0;
                arr[high]=1;
                low++;
                high--;
            }
        }
    }
