# Group 59
* Yige Yang, uni: yy3266
* Yucheng Lu, uni: yl5163

* PostgreSQL account name: yy3266

* URL of web application: http://34.139.100.66:8111

**notice**: make sure the version of sqlalchemy == 1.4

# Little_A

## Proposal

* The application it to mimic the simplest part of online shopping on Amazon line. 
* five entities:
  1. customer: has a unique customer ID, first and last names, addresses, e-mail, phone numbers, membership statuses, preferences, and password. After the customer login, they can purchase multiple orders or cancel them. The customer can also review the product they ordered by rating stars.
  2. product: has the product name, unit price, dimensions, weight, and manufacturer. The product belongs to exactly one category.
  3. order: has the order ID, customer ID, product ID, number of products ordered, and order date. Every other must contain at least one product. The order is canceled or purchased by exactly one customer with specific reasons.
  4. category: has category_ID and category name, which contains the product. The category uniquely sorts different types of products.
  5. seller: has seller_ID, their names, and the product ID. They can sell one or more products.

## User Interaction 
1. Create Account
* Once the customer clicks signup, its information will store into Customer table. Meanwhile, the cutomer table will give the customer a customer_id.
* (If the format of password is not correct and the email is used, the registration will fail.)
* Then, the customer can log in with the input of first_name, last_name, email, and password.
* Customer can click Account to see their profile.

2. Add to cart
* Under each category, there are one and more products
* For each product, there is a seller
* The customer can add one and more different products from different category into cart

3. Payment
* Customer can click Submit Payment and choose payment method
* Then, the web page will show "payment successful"
* The order history will update
* Customer can click "Cancel Order", and the order status will become from "processing" to "canceled".
* Customer can select cancellation reason: "I do not want it", or "Order the wrong product"
* Customer can review the products ordered with review rating

### Missing function
* Customer is not able to delete the product they added in the cart, because this application does not have cart table. It can not store the products added in the cart.
* This application does not have "search" function. The customer is not able to search the keyword for products.
* This application can not provide the recommendation for customer based on order history because there is no recommendation table

### Interesting Web Page -- Add to Cart & Order History
* add to cart web page:
  * it is related to category, product, and order_info database
  * customer can select different types of products and select the number of products from category and product database
  * after the customer pays, the cart information will be stored in order_info database

* order history:
  * it is related to customer, category, product, and order_info database
  * the order history will show orders in which contain one and more products from order_info table
  * "total price": select the quantity of product and multipy by the unit-price from product database



