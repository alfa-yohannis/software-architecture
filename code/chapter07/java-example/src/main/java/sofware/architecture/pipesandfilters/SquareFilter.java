package sofware.architecture.pipesandfilters;

import java.util.ArrayList;
import java.util.List;

// Filter 2: Filter to square the numbers
class SquareFilter implements Filter {
    public List<Integer> filter(List<Integer> numbers) {
        List<Integer> squaredNumbers = new ArrayList<>();
        for (int num : numbers) {
            squaredNumbers.add(num * num);
        }
        return squaredNumbers;
    }
}