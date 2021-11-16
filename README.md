# azure-cosmos-function
* Multi function trigger on Comsos create

```
curl -X POST -H "content-type: application/json" -d '{ "num": 3 }' "https://cosmfun<RANDOM>.azurewebsites.net/api/InsertRowsHttpTrigger?code=<KEY>"
```