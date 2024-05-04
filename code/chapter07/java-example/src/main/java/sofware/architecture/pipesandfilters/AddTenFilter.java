package sofware.architecture.pipesandfilters;

import java.util.ArrayList;
import java.util.List;

public class AddTenFilter implements Filter {

	@Override
	public List<Integer> filter(List<Integer> numbers) {
		List<Integer> addBy10Numbers = new ArrayList<>();
        for (int num : numbers) {
            addBy10Numbers.add(num + 10);
        }
        return addBy10Numbers;
	}

}
