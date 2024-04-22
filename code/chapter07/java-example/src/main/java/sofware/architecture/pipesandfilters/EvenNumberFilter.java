package sofware.architecture.pipesandfilters;

import java.util.ArrayList;
import java.util.List;


class EvenNumberFilter implements Filter {
    public List<Integer> filter(List<Integer> numbers) {
        List<Integer> filteredNumbers = new ArrayList<>();
        for (int num : numbers) {
            if (num % 2 == 1) {
                filteredNumbers.add(num);
            }
        }
        return filteredNumbers;
    }
}
