const EventEmitter = require('events');
const Twilio = require('twilio');

const accountSid = 'AC0cca4d377c439150f319a3eb3766d11b';
const authToken = '2f3f837ac810eb49c1e86e79bcb7b8fd';

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
      from: '+12543213976',
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
    name: 'Glenny',
    phone: '+6285777505255',
  },
  items: [
    { name: 'Item 1', price: 10 },
    { name: 'Item 2', price: 20 },
  ],
  total: 30,
};

placeOrder(exampleOrder);