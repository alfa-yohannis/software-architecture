/***
* Copyright (c) 2023 Alfa Yohannis
* 
* Permission is hereby granted, free of charge, to any person obtaining a copy 
* of this software and associated documentation files (the "Software"), 
* to deal in the Software without restriction, including without limitation 
* the rights to use, copy, modify, merge, publish, distribute, sublicense, 
* and/or sell copies of the Software, and to permit persons to whom the Software 
* is furnished to do so, subject to the following conditions:
* 
* The above copyright notice and this permission notice shall be included in 
* all copies or substantial portions of the Software.
* 
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
* INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR 
* A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
* COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER 
* IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION 
* WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
***/

package pradita.softwarearchitecture;

import java.io.IOException;

import javafx.beans.property.DoubleProperty;
import javafx.beans.property.SimpleDoubleProperty;
import javafx.beans.property.SimpleStringProperty;
import javafx.beans.property.StringProperty;
import javafx.beans.value.ChangeListener;
import javafx.beans.value.ObservableValue;

public class ConverterViewModel {

	private StringProperty fromCurrency = new SimpleStringProperty();
	private StringProperty toCurrency = new SimpleStringProperty();
	private DoubleProperty fromValue = new SimpleDoubleProperty(1.0);
	private DoubleProperty toValue = new SimpleDoubleProperty();

	public ConverterViewModel() {

		ChangeListener<Object> changeListener = new ChangeListener<Object>() {
			@Override
			public void changed(ObservableValue<? extends Object> obsevervableValue, Object oldVal, Object newVal) {
				try {
					ConverterViewModel.this.update();
				} catch (IOException e) {
					e.printStackTrace();
				}
			}
		};
		fromCurrency.addListener(changeListener);
		toCurrency.addListener(changeListener);
		fromValue.addListener(changeListener);
	}

	public StringProperty getFromCurrency() {
		return fromCurrency;
	}

	public StringProperty getToCurrency() {
		return toCurrency;
	}

	public DoubleProperty getFromValue() {
		return fromValue;
	}

	public DoubleProperty getToValue() {
		return toValue;
	}

	void update() throws IOException {
		if (toCurrency.getValue() == null || fromCurrency.getValue() == null || fromValue.getValue() == null) {
			return;
		}

		Thread t = new Thread() {
			public void run() {
				double rate = ConverterService.getRate(fromCurrency.get(), toCurrency.get());
				toValue.set(rate * fromValue.get());
			}
		};
		t.start();
	}

}
