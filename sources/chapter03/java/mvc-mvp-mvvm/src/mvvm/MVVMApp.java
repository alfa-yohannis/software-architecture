package mvvm;

public class MVVMApp {

	public static void main(String[] args) {

		try {
			Model model = new Model("Model-1");

			ViewModel viewModel = new ViewModel();
			viewModel.setModel(model);

			viewModel.getViewModelProperties().put("spinner001", new ViewModelProperty("spinner001", viewModel));
			viewModel.getViewModelProperties().put("spinner002", new ViewModelProperty("spinner002", viewModel));
			viewModel.getViewModelProperties().put("spinner003", new ViewModelProperty("spinner003", viewModel));
			viewModel.getViewModelProperties().put("spinner001b", new ViewModelProperty("spinner001b", viewModel));
			viewModel.getViewModelProperties().put("spinner002b", new ViewModelProperty("spinner002b", viewModel));
			viewModel.getViewModelProperties().put("spinner003b", new ViewModelProperty("spinner003b", viewModel));

			View view = new View();
			view.setVisible(true);

			view.bind(viewModel);
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

}
