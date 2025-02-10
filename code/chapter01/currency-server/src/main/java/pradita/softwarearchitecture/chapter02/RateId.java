package pradita.softwarearchitecture.chapter02;

import java.io.Serializable;

public class RateId implements Serializable {
  private String fromCurrency;
  private String toCurrency;


  public String getFromCurrency() {
    return this.fromCurrency;
  }

  public void setFromCurrency(String fromCurrency) {
    this.fromCurrency = fromCurrency;
  }

  public String getToCurrency() {
    return this.toCurrency;
  }

  public void setToCurrency(String toCurrency) {
    this.toCurrency = toCurrency;
  }

}
