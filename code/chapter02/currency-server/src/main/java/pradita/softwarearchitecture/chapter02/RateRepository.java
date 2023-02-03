package pradita.softwarearchitecture.chapter02;

import java.util.Collection;

//import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.CrudRepository;



public interface RateRepository extends CrudRepository<Rate, Integer> {
  
  //JPQL
  //@Query("SELECT r FROM Rate r WHERE r.fromCurrency = ?1 and r.toCurrency = ?2")
  Collection<Rate> findFirstByFromCurrencyAndToCurrency(String fromCurrency, String toCurrency);
  
}