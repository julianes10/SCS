echo "Test GET status..."
curl -i http://localhost:5060/api/v1.0/timelapse/status


echo "Test POST new timelapse..."
curl -i -H "Content-Type: application/json" -X POST -d '{"name":"new","status":"ONGOING","interval":2,"maxNbrOfPictures":5}' http://localhost:5060/api/v1.0/timelapse/ongoing/new


echo "Test POST stop video. Generate it and clean photos"
curl -i http://localhost:5060/api/v1.0/timelapse/ongoing/stop


echo "Test POST take a look nor stopping neither cleaning"
curl -i http://localhost:5060/api/v1.0/timelapse/ongoing/peek


echo "Test POST cancel ongoing. Do no generate video, just clean and stop"
curl -i http://localhost:5060/api/v1.0/timelapse/ongoing/cancel


echo "Test POST create video, delete intermediates..."

echo "Test POST create video, but keep intermediates..."

echo "Test POST new tracker atleti.."
#curl -i -H "Content-Type: application/json" -X POST -d '{ "content":[ {"keystrings":["football","atletico","madrid"]} ] }' http://localhost:5057/api/v1.0/kodi/tracker

 

