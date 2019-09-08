
BASE_URL="http://localhost:5061/api/v1.0/telegramBOT"


echo "Test GET status..."
curl -i $BASE_URL/status


#echo "Test POST new tracker with empty content..."
#curl -i -H "Content-Type: application/json" -X POST -d '{ "content":[ ] }' http://localhost:5057/api/v1.0/kodi/tracker


echo "Test POST new event with predefined action..."
curl -i -H "Content-Type: application/json" -X POST -d '{"name":"pepito1", "action":"foto"}' curl -i $BASE_URL/event


echo "Test POST new event with explicit text..."
curl -i -H "Content-Type: application/json" -X POST -d '{"name":"pepito2", "text":"This is the event text"}' curl -i $BASE_URL/event

echo "Test POST new event with explicit text and predefined action..."
curl -i -H "Content-Type: application/json" -X POST -d '{"name":"pepito3", "text":"This is the event text", "action":"foto"}' curl -i $BASE_URL/event
 

