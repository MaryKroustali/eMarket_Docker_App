# Ergasia2_e18084
## MongoDB
Για την υλοποίηση του παρακάτω πληροφοριακού συστήματος σε Python χρησιμοποιήθηκε Flask server για την υλοποίηση του web service και MongoDB για την αποθήκευση δεδομένων.
</br>
Αρχικά, δημιουργήθηκε ένα container της MongoDB με όνομα mongodb1 με την παρακάτω εντολή:

```docker run -d -p 27017:27017 --name mongodb1 mongo:4.0.4```

Η δημιουργία της βάσης δεδομένων και των collection της έγινε αυτόματα από τον python κώδικα
```
   client = MongoClient('mongodb://localhost:27017/') # Connect to MongoDB
   db = client['DSMarkets'] # Create database
   users = db['Users'] # Create collections
   products = db['Products'] 
```
## Web service
### Entrypoint: Create account
Με το συγκεκριμένο entrypoint γίνεται η εγγραφή ενός χρήστη στο σύστημα με το ονοματεπώνυμό του, το email του και ένα password. Γίνεται αναζήτηση του email που έδωσε ο χρήστης 
αν υπάρχει ήδη στη βάση, ως εγγρεγραμμένος, ```users.find({"e-mail":data["e-mail"]}).count() == 0 ```, ώστε να ειδοποιηθεί με κατάλληλο μήνυμα.

Αν το email δεν υπάρχει, τότε επισυνάπτεται αυτόματα στα στοιχεία του χρήστη η ένδειξη "simple user"
``` 
    category = {'category':'simple user'}
    data.update(category)
```
και, τέλος, εισάγεται στην βάση, ```users.insert_one(data)```.

Παρακάτω παρουσιάζεται η υλοποίηση του entrypoint. Αρχικά, για 2 χρήστες με επιτυχία και έπειτα για χρήστη με email πoυ υπάρχει ήδη στη βάση.

<img src="screenshots/createSimpleUser.png">

### Entrypoint: Login
Το entrypoint αναφέρεται στην σύνδεση χρήστη στο σύστημα. Συγκεκριμένα, ο χρήστης δίνει το email του και το password που όρισε κατά την εγγραφή του. Πραγματοποιέιται αναζήτηση 
στη βάση με αυτά ```users.find_one({"e-mail":data["e-mail"], "password":data["password"]})``` και αν βρεθεί ο χρήστης, τότε καλέιται η συνάρτηση create_session() με παράμετρο το 
email του χρήστη. 

Η συνάρτηση create_session() δημιουργεί έναν κωδικό αυθεντικοποίησης που επιστρέφεται στον χρήστη μετά από επιτυχημένη σύνδεση στο σύστημα ώστε να χρησιμοποιεί τις υπηρεσίες του 
super market. Αν τα στοιχεία που εισήγαγε ο χρήστης είναι λανθασμένα, επιστρέφεται κατάλληλο μήνυμα.

Παρακάτω παρουσιάζεται η υλοποίηση του endpoint. Αρχικά γίνεται επιτυχημένη σύνδεση και έπειτα δίνεται λάθος password και λάθος email.

<img src="screenshots/login.png">

*Για όλα τα παρακάτω endpoints απαιτείται η σύνδεση του χρήστη στο σύστημα. Για κάθε curl, εντολή εκτέλεσης, ο χρήστης δίνει τον κωδικό αυθεντικοποίησης του στο header.*

### Entrypoint: Get product 
Μέσω αυτού του enrtypoint ο χρήστης μπορεί να αναζητά προϊόντα με βάση το όνομα προϊόντος, την κατηγορία του ή το μοναδικό κωδικό του. Ανάλογα με το στοιχείο που εισάγει ο 
χρήστης εκτελείται το αντίστοιχο query αναζήτησης. 

Στην περίπτωση αναζήτησης βάσει ονόματος εκτεκλείται: ```products.find({'name':data["name"]})```. Αν βρεθεί ένα η παραπάνω προϊόντα τότε αποθηκεύονται σε πίνακα με σκοπό αυτός 
να ταξινομήθει με βάση τα ονόματα των προϊόντων, ```sorted(productsArray, key = lambda i: i['name'])```

Στην περίπτωση αναζήτησης βάσει κατηγορίας εκτελείται το query ```products.find({'category':data["category"]})```. Αν βρεθούν αποτελέσματα, δημιουργείται πίνακας όπου 
αποθηκέυονται τα προϊόντα και, στην συνέχεια, ταξινομείται με βάση την τιμή αυτών, ```sorted(productsArray, key = lambda i: i['price'])```. 

Στην περίπτωση αναζήτησης με το id του προϊόντος, εκτελείται ```products.find_one({'id':data["id"]})```. Επειδή το id είναι μοναδικό για κάθε προιόν, επιστρέφεται πάντα ένα 
αποτέλεσμα. 

Όλα τα παραπάνω επιστρέφουν για κάθε προϊόν το όνομα, την περιγραφή, την τιμή, την κατηγορία και τον κωδικό του, 
```{'name':product["name"],'description':product["description"],'price': product["price"],'category':product["category"],'id':product["id"]}``` 
Επιπλέον, σε περίπτωση που δε βρεθεί κανένα προϊόν για τις παραπάνω αναζητήσεις επιστρέφεται κατάλληλο μήνυμα. 

Η υλοποίηση του entrypoint περιλαμβάνει τρεις επιμέρους αναζητήσεις:

-Με βάση όνομα προϊόντος:
<img src="screenshots/getProductName.png">

-Με βάση κατηγορία προϊόντος:
<img src="screenshots/getProductCategory.png">

-Με βάση τον κωδικό προϊόντος:
<img src="screenshots/getProductId.png">


### Entrypoint: Add product to cart
### Entrypoint: Get cart
### Entrypoint: Delete product from cart
### Entrypoint: Buy products
### Entrypoint: Get order history
### Entrypoint: Delete account
<!--admin does not login-->
### Entrypoint: Add product 
### Entrypoint: Delete product
### Entrypoint: Update product

## Containerize
