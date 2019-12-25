echo "Test trigger hotword..."
curl -i -H "Content-Type: application/json" -X POST -d '{ "pan": { "abs" : "0" } }' http://localhost:5000/ipadispatcher/api/v1.0/hotword
echo "Test trigger direclty a dispatch.."

curl -i -H "Content-Type: application/json" -X POST -d '{ "request": "light color red" }' http://localhost:5000/ipadispatcher/api/v1.0/dispatch
