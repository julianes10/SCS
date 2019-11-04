echo "Test GET status..."
curl -i http://localhost:5070/api/v1.0/picam/status


echo "Test POST new tracker with empty content..."

curl -i -H "Content-Type: application/json" -X POST -d '{ "pan": { "abs" : "0" } }' http://localhost:5070/api/v1.0/picam/position
curl -i -H "Content-Type: application/json" -X POST -d '{ "pan": { "abs" : "70" } }' http://localhost:5070/api/v1.0/picam/position
curl -i -H "Content-Type: application/json" -X POST -d '{ "pan": { "delta" : "30" } }' http://localhost:5070/api/v1.0/picam/position
curl -i -H "Content-Type: application/json" -X POST -d '{ "pan": { "delta" : "10" } }' http://localhost:5070/api/v1.0/picam/position


curl -i -H "Content-Type: application/json" -X POST -d '{ "tilt": { "abs" : "0" } }' http://localhost:5070/api/v1.0/picam/position
curl -i -H "Content-Type: application/json" -X POST -d '{ "tilt": { "abs" : "70" } }' http://localhost:5070/api/v1.0/picam/position
curl -i -H "Content-Type: application/json" -X POST -d '{ "tilt": { "delta" : "-30" } }' http://localhost:5070/api/v1.0/picam/position
curl -i -H "Content-Type: application/json" -X POST -d '{ "tilt": { "delta" : "10" } }' http://localhost:5070/api/v1.0/picam/position

