# Ergasia2_e18084
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
