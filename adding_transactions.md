## adding transactions
In some circumstances it makes sense to think about performance in terms of transactions which means capturing the elapsed time across several requests.
To assist with this, there is a Transaction Manager in [plugins](./examples/plugins).
An full example is provided in [examples](./examples)
There are two functions:
   start_transaction
   end_transaction

```python
#when starting a transaction save the id returned as a variable to be used to end the transaction
self.startup = tm.start_transaction("startup")
...

#when ending a transaction use the id you captured (in this case self.startup)
tm.end_transaction(self.startup)
```

## getting the results
There are two endpoints:

   /stats/transactions/csv   
   To get summary stats (like /stats/transactions/csv)

   /stats/transactions/all/csv   
   To get all results

## running headless
if you want to run the test headess, you can get the results by adding the command line argument --log_transactions_in_file True
by default it will be False