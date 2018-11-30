echo "Test GET all tasks..."
curl -i http://localhost:5000/todo/api/v1.0/tasks
echo "Test GET task individuals that exist..."
curl -i http://localhost:5000/todo/api/v1.0/tasks/1
curl -i http://localhost:5000/todo/api/v1.0/tasks/2
echo "Test GET task individual that not exist..."
curl -i http://localhost:5000/todo/api/v1.0/tasks/1444
echo "Test POST create new 2 tasks..."
curl -i -H "Content-Type: application/json" -X POST -d '{"title":"Read a book"}' http://localhost:5000/todo/api/v1.0/tasks
curl -i -H "Content-Type: application/json" -X POST -d '{"title":"Read a bo5555ok"}' http://localhost:5000/todo/api/v1.0/tasks
echo "Test GET all tasks again..."
curl -i http://localhost:5000/todo/api/v1.0/tasks
echo "Test DELETE a task..."
curl -i -H "Content-Type: application/json" -X DELETE http://localhost:5000/todo/api/v1.0/tasks/1
curl -i http://localhost:5000/todo/api/v1.0/tasks/1
echo "Test CHANGE a task..."
curl -i -H "Content-Type: application/json" -X PUT -d '{"description":"description changed"}' http://localhost:5000/todo/api/v1.0/tasks/2
curl -i http://localhost:5000/todo/api/v1.0/tasks/2
