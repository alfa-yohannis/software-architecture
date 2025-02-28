package mvc;

public class MVCApp {

	public static void main(String[] args) {

		try {
			Model model = new Model("001");
			View view = new View();
			view.setName("001");
			view.setVisible(true);
			model.setView(view);
			
			Controller.getModels().put(model.getName(), model);
			
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

}
