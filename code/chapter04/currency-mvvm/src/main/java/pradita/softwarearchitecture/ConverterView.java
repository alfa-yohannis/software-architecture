package pradita.softwarearchitecture;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import javafx.beans.binding.Bindings;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.scene.control.ComboBox;
import javafx.scene.control.TextField;
import javafx.util.StringConverter;
import javafx.util.converter.DoubleStringConverter;

public class ConverterView {

	@FXML
	private ComboBox<String> comboBoxFrom;

	@FXML
	private ComboBox<String> comboBoxTo;

	@FXML
	private TextField textFieldFrom;

	@FXML
	private TextField textFieldTo;

	private ConverterViewModel viewModel = new ConverterViewModel();

	@SuppressWarnings("unchecked")
	@FXML
	public void initialize() {
		List<String> currencies = new ArrayList<>();
		currencies.addAll(Arrays.asList(new String[] { "USD", "GBP", "IDR" }));
		comboBoxFrom.getItems().setAll(currencies);
		comboBoxTo.getItems().setAll(currencies);

		StringConverter<? extends Number> converter = new DoubleStringConverter();

		Bindings.bindBidirectional(comboBoxFrom.valueProperty(), viewModel.getFromCurrency());
		Bindings.bindBidirectional(comboBoxTo.valueProperty(), viewModel.getToCurrency());
		Bindings.bindBidirectional(textFieldFrom.textProperty(), viewModel.getFromValue(),
		    (StringConverter<Number>) converter);
		Bindings.bindBidirectional(textFieldTo.textProperty(), viewModel.getToValue(), (StringConverter<Number>) converter);

	}

	@FXML
	void onFromCurrencySelected(ActionEvent event) {
		System.out.println(viewModel.getFromCurrency().getValue());

	}

	@FXML
	void onToCurrencySelected(ActionEvent event) {
		System.out.println(viewModel.getToCurrency().getValue());
	}

}
