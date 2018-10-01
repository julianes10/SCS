echo "Test GET status..."
curl -i http://localhost:5057/api/v1.0/kodi/status


echo "Test POST new tracker with empty content..."
curl -i -H "Content-Type: application/json" -X POST -d '{ "content":[ ] }' http://localhost:5057/api/v1.0/kodi/tracker


echo "Test POST new tracker totally empty..."
curl -i -H "Content-Type: application/json" -X POST -d '{"fake":"fake"}' http://localhost:5057/api/v1.0/kodi/tracker

echo "Test POST new tracker atleti.."
curl -i -H "Content-Type: application/json" -X POST -d '{ "content":[ {"keystrings":["football","atletico","madrid"]} ] }' http://localhost:5057/api/v1.0/kodi/tracker

 

