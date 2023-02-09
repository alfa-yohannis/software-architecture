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

package pradita.softwarearchitecture.chapter02;

import java.util.Collection;
import java.util.HashMap;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
public class CurrencyController {

	@Autowired
	private RateRepository rateRepository;

	@GetMapping(value = "/")
	public String convert(Double value, String from, String to, Model model) {

		if (value == null)
			value = 1.0;
		if (from == null)
			from = "USD";
		if (to == null)
			to = "IDR";

		Double toValue = 0.0;
		Rate rate = rateRepository.findFirstByFromCurrencyAndToCurrency(from, to).iterator().next();
		if (rate != null)
			toValue = value * rate.getRate();

		model.addAttribute("value", value);
		model.addAttribute("from", from);
		model.addAttribute("to", to);
		model.addAttribute("toValue", toValue);
		model.addAttribute("fromCurrencies", rateRepository.findAllFromCurrency());
		model.addAttribute("toCurrencies", rateRepository.findAllToCurrency());

		return "converter";
	}

	/**
	 * http://localhost:8080/addrate?from=USD&to=IDR&rate=15000
	 * 
	 * @param from
	 * @param to
	 * @param rate
	 * @return
	 */
	@GetMapping(value = "/addrate")
	String addRate(String from, String to, Double rate, Model model) {

		if (from == null || to == null || rate == null)
			return "addrate";

		Rate r = rateRepository.save(new Rate(from, to, rate));

		if (r != null) {
			model.addAttribute("success", true);
		} else {
			model.addAttribute("success", false);
		}

		return "addrate";
	}

}
