package sofware.architecture.pipesandfilters;

import java.util.List;

class Pipeline {
    private final List<Filter> filters;

    public Pipeline(List<Filter> filters) {
        this.filters = filters;
    }

    public List<Integer> process(List<Integer> data) {
    	System.out.println("Input: " + data);
        List<Integer> result = data;
        for (Filter filter : filters) {
            result = filter.filter(result);
            System.out.println("Temp Result: " + result);
        }
        return result;
    }
}