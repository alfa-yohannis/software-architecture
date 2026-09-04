package pradita.softwarearchitecture.chapter02;

import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.IdClass;

@Entity
@IdClass(RateId.class)
public class Rate {

  @Id
  private String fromCurrency;
  @Id
  private String toCurrency;
  private Double rate;

  Rate(){
    super();
  }
  Rate(String fromCurrency, String toCurrency, Double rate) {
    super();
    this.fromCurrency = fromCurrency;
    this.toCurrency = toCurrency;
    this.rate = rate;
  }

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

  public Double getRate() {
    return this.rate;
  }

  public void setRate(Double rate) {
    this.rate = rate;
  }

}
