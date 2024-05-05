package software.architecture.soa.entity;

import java.util.ArrayList;
import java.util.List;

// Order.java
class Order {
    private List<OrderLineItem> lineItems;

    public Order() {
        this.lineItems = new ArrayList<>();
    }

    public List<OrderLineItem> getLineItems() {
        return lineItems;
    }

    public void addLineItem(OrderLineItem lineItem) {
        lineItems.add(lineItem);
    }
}


