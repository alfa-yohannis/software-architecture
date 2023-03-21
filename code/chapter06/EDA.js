const EventEmitter = require('events');
const Twilio = require('twilio');

const accountSid = 'AC9e74af22079885e326bfbd0c836e0ce0';
const authToken = '54960f4f27f0f48187754e33cde507ce';

// Create event emitter
const eventEmitter = new EventEmitter();

// Function to place an order
function placeOrder(order) {
  // ... code to place the order ...

  // Emit the 'orderPlaced' event
  eventEmitter.emit('orderPlaced', order);
}
  
// Function to send notification via Twilio
function sendNotification(order) {
  const client = new Twilio(accountSid, authToken);
  const messageBody = `New order received: ${order.id}`;

  client.messages
    .create({
      body: messageBody,
      to: order.customer.phone,
      from: '+12764001666',
    })
    .then((message) => {
      console.log(`Notification sent: ${message.sid}`);
    })
    .catch((error) => {
      console.error(`Notification error: ${error}`);
    });
}

// Listen for the 'orderPlaced' event and send a notification
eventEmitter.on('orderPlaced', (order) => {
  sendNotification(order);
});

// Example usage
const exampleOrder = {
  id: 123,
  customer: {
    name: 'Delvin',
    phone: '+6281270763110',
  },
  items: [
    { name: 'Item 1', price: 10 },
    { name: 'Item 2', price: 20 },
  ],
  total: 30,
};

placeOrder(exampleOrder);