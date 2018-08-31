echo "Test GET status..."
curl -i http://localhost:5001/api/v1.0/ls/status

echo "Test POST new debug on..."
curl -i -H "Content-Type: application/json" -X POST -d '{"debug":true}' http://localhost:5001/api/v1.0/ls/debug

echo "Test POST new color..."
curl -i -H "Content-Type: application/json" -X POST -d '{"color":"red"}' http://localhost:5001/api/v1.0/ls/color


echo "Test POST new timeout..."
curl -i -H "Content-Type: application/json" -X POST -d '{"timeout":200}' http://localhost:5001/api/v1.0/ls/timeout


echo "Test POST new pause..."
curl -i -H "Content-Type: application/json" -X POST -d '{"pause":2000}' http://localhost:5001/api/v1.0/ls/pause


echo "Test POST new mode..."
curl -i -H "Content-Type: application/json" -X POST -d '{"mode":"T"}' http://localhost:5001/api/v1.0/ls/mode

echo "Test POST misc..."
curl -i -H "Content-Type: application/json" -X POST -d '{"mode":"K", "color":"blue"}' http://localhost:5001/api/v1.0/ls/misc


echo "Test POST new debug off.."
curl -i -H "Content-Type: application/json" -X POST -d '{"debug":false}' http://localhost:5001/api/v1.0/ls/debug

echo "Test POST movement Forward..."
curl -i -H "Content-Type: application/json" -X POST -d '{"mode":"F"}' http://localhost:5001/api/v1.0/ce/mode

echo "Test POST slight turn left..."
curl -i -H "Content-Type: application/json" -X POST -d '{"raw":"L"}' http://localhost:5001/api/v1.0/ce/steeringWheel

echo "Test POST gas speed..."
curl -i -H "Content-Type: application/json" -X POST -d '{"raw":"G"}' http://localhost:5001/api/v1.0/ce/speed

echo "Test POST specific speed..."
curl -i -H "Content-Type: application/json" -X POST -d '{"value":300}' http://localhost:5001/api/v1.0/ce/speed

echo "Test GET ce status..."
curl -i -H "Content-Type: application/json" http://localhost:5001/api/v1.0/ce/status
