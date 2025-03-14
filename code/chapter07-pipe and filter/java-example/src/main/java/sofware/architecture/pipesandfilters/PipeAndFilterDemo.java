package sofware.architecture.pipesandfilters;

import java.util.List;

public class PipeAndFilterDemo {
	public static void main(String[] args) {
		// Input data
		List<Integer> numbers = List.of(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);

		// Define filters
		Filter oddNumberFilter = new EvenNumberFilter();
		Filter multiplyBy3Filter = new MultiplyBy3Filter();
		Filter addTenFilter = new AddTenFilter();

		// Create a pipeline
		Pipeline pipeline = new Pipeline(List.of(oddNumberFilter, 
				multiplyBy3Filter, addTenFilter));

		// Process the data through the pipeline
		List<Integer> result = pipeline.process(numbers);

		// Output the result
		System.out.println("Result: " + result);
	}
}
