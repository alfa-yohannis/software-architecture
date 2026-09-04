package mvc;

import java.util.HashMap;
import java.util.Map;

public class Controller {

	private static Map<String, Model> models = new HashMap<>();

	public static void handleChange(String modelName, String spinnerName, int value) {
//		System.out.println(spinnerName + ", value:" + value);
		Model model = models.get(modelName);
		model.setValue(spinnerName, value);
	}

	public static Map<String, Model> getModels() {
		return models;
	}

	public static void setModels(Map<String, Model> models) {
		Controller.models = models;
	}

}
