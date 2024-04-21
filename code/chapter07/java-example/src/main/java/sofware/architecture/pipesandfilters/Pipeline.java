package sofware.architecture.pipesandfilters;

import java.util.List;

// Step 2: Define the pipeline to connect the filters
class Pipeline {
    private final List<Filter> filters;

    public Pipeline(List<Filter> filters) {
        this.filters = filters;
    }

    public List<Integer> process(List<Integer> data) {
        List<Integer> result = data;
        for (Filter filter : filters) {
            result = filter.filter(result);
        }
        return result;
    }
}