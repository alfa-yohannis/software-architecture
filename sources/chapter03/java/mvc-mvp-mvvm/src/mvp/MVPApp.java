package mvp;

public class MVPApp {

    public static void main(String[] args) {

        try {
            Model model = new Model("Model-1");

            Presenter presenter = new Presenter();
            presenter.setModel(model);

            View view = new View();
            view.setVisible(true);

            presenter.setView(view);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

}
