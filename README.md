\# People's Cart 🛒



A full-stack e-commerce web application built with Django, MySQL, HTML, CSS, and JavaScript.



\## Features



\* User registration and login

\* Product listing and product details

\* Product search

\* Category filtering

\* Shopping cart

\* Add, update, and remove cart items

\* Stock availability and stock-limit validation

\* Checkout and order creation

\* Order history and order tracking

\* Admin dashboard

\* Admin order-status management

\* Django Admin product and category management

\* Responsive UI



\## Tech Stack



\*\*Frontend\*\*



\* HTML5

\* CSS3

\* JavaScript



\*\*Backend\*\*



\* Python

\* Django



\*\*Database\*\*



\* MySQL



\*\*Tools\*\*



\* Git

\* GitHub

\* VS Code



\## Project Structure



```text

E-commerce/

├── ecommerce/

├── store/

├── manage.py

├── .gitignore

└── README.md

```



\## Installation



\### 1. Clone the repository



```bash

git clone https://github.com/sanjaykumar36/Ecomerce-website.git

cd Ecomerce-website

```



\### 2. Create virtual environment



```bash

python -m venv venv

```



\### 3. Activate virtual environment



```bash

venv\\Scripts\\activate

```



\### 4. Install dependencies



```bash

pip install django pillow mysqlclient

```



\### 5. Configure MySQL



Create the database:



```sql

CREATE DATABASE ecommerce\_db;

```



Configure your local MySQL credentials in `ecommerce/settings.py`.



\### 6. Run migrations



```bash

python manage.py migrate

```



\### 7. Create admin user



```bash

python manage.py createsuperuser

```



\### 8. Start the server



```bash

python manage.py runserver

```



Open:



```text

http://127.0.0.1:8000/

```



Admin:



```text

http://127.0.0.1:8000/admin/

```



\## Main Modules



\### Customer



\* Registration and login

\* Product browsing

\* Search and category filtering

\* Cart management

\* Checkout

\* Order history

\* Order status tracking

\* Profile management



\### Admin



\* Product management

\* Category management

\* Order management

\* Order status updates

\* Customer order monitoring



\## Future Enhancements



\* Online payment integration

\* Product reviews and ratings

\* Wishlist

\* Pagination

\* Email notifications

\* REST API

\* Cloud deployment



\## Author



\*\*Sanjay Kumar\*\*



GitHub: https://github.com/sanjaykumar36



\## Project



People's Cart — Full-Stack Django E-commerce Website



