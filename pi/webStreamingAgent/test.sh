echo "Test GET status..."
curl -i http://localhost:5060/api/v1.0/webStreamingAgent/status


echo "Test POST new tracker with empty content..."
curl -i -H "Content-Type: application/json" -X POST -d '{ "channel":"www.google.es"}' http://localhost:5060/api/v1.0/webStreamingAgent/tracker


echo "Test POST new tracker totally empty..."
curl -i -H "Content-Type: application/json" -X POST -d '{"channel":""}' http://localhost:5060/api/v1.0/webStreamingAgent/tracker


curl -i -H "Content-Type: application/json" -X POST -d '{ "channel":"mitele.es/directo/movistar-laliga"}' http://192.168.1.42:5060/api/v1.0/webStreamingAgent/tracker


 

