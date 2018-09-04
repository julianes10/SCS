echo "Test GET status..."
curl -i http://localhost:5056/api/v1.0/dht/status

echo "Test GET sensors..."
curl -i http://localhost:5056/api/v1.0/dht/sensors/now

