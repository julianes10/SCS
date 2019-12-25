params=$@
echo "params: $params"
curl -i -H "Content-Type: application/json" -X POST -d '{ "request": "'"$params"'" }'  http://localhost:5000/ipadispatcher/api/v1.0/dispatch
