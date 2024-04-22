package sofware.architecture.pipesandfilters;

import java.util.ArrayList;
import java.util.List;

class MultiplyBy3Filter implements Filter {
    public List<Integer> filter(List<Integer> numbers) {
        List<Integer> squaredNumbers = new ArrayList<>();
        for (int num : numbers) {
            squaredNumbers.add(num * 3);
        }
        return squaredNumbers;
    }
}