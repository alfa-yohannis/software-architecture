package sofware.architecture.pipesandfilters;

import java.util.ArrayList;
import java.util.List;

class MultiplyBy3Filter implements Filter {
	
    public List<Integer> filter(List<Integer> numbers) {
        List<Integer> multipliedBy3Numbers = new ArrayList<>();
        for (int num : numbers) {
            multipliedBy3Numbers.add(num * 3);
        }
        return multipliedBy3Numbers;
    }
}