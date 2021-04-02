HOSTHYP=$1
PORTHYP=$2


echo "Test hyperion api..."
curl -i -H "Content-Type: application/json" -X POST -d '{    "command":"serverinfo",    "tan":1 }' http://$HOSTHYP:$PORTHYP/json-rpc


