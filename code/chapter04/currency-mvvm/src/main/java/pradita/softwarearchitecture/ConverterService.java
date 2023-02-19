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

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

public class ConverterService {

	private static ObjectMapper mapper = new ObjectMapper();

	public static double getRate(String fromCurrency, String toCurrency) {
		try {
			OkHttpClient client = new OkHttpClient().newBuilder().build();

			String url = "https://api.apilayer.com/exchangerates_data/convert?" //
			    + "to=" + toCurrency //
			    + "&from=" + fromCurrency//
			    + "&amount=1";
			Request request = new Request.Builder().url(url).addHeader("apikey", "a0TThcO3Z3TAuaJd0JiGcvpjRzPlEHm0")
			    .method("GET", null).build();
			Response response = client.newCall(request).execute();

			JsonNode node = mapper.readTree(response.body().string());
			Double rate = node.get("info").get("rate").asDouble();

			return rate;

		} catch (java.net.SocketTimeoutException e) {
			System.out.println(e.getMessage());
		} catch (JsonMappingException e) {
			System.out.println(e.getMessage());
		} catch (JsonProcessingException e) {
			System.out.println(e.getMessage());
		} catch (IOException e) {
			System.out.println(e.getMessage());
		}
		return 0;
	}
}
