package sofware.architecture.pipesandfilters;

import java.util.ArrayList;
import java.util.List;


class OddNumberFilter implements Filter {
    public List<Integer> filter(List<Integer> numbers) {
        List<Integer> filteredNumbers = new ArrayList<>();
        for (int num : numbers) {
            if (num % 2 == 0) {
                filteredNumbers.add(num);
            }
        }
        return filteredNumbers;
    }
}
