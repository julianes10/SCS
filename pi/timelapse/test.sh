echo "Test GET status..."
curl -i http://localhost:5060/api/v1.0/timelapse/status


echo "Test POST new project..."
#curl -i -H "Content-Type: application/json" -X POST -d '{ "content":[ ] }' http://localhost:5057/api/v1.0/kodi/tracker


echo "Test POST delete complete a project: stop, clean photo and videos..."
#curl -i -H "Content-Type: application/json" -X POST -d '{"fake":"fake"}' http://localhost:5057/api/v1.0/kodi/tracker

echo "Test POST create video, delete intermediates..."

echo "Test POST create video, but keep intermediates..."

echo "Test POST new tracker atleti.."
#curl -i -H "Content-Type: application/json" -X POST -d '{ "content":[ {"keystrings":["football","atletico","madrid"]} ] }' http://localhost:5057/api/v1.0/kodi/tracker

 

