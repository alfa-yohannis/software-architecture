package software.architecture.soa.entity;
// OrderLineItem.java
class OrderLineItem {
    private Item item;
    private int quantity;

    public OrderLineItem(Item item, int quantity) {
        this.item = item;
        this.quantity = quantity;
    }

    public Item getItem() {
        return item;
    }

    public int getQuantity() {
        return quantity;
    }
}
