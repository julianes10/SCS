HOSTHYP="192.168.1.55"
PORTHYP="8090"

prio=$3
foo=$(cat <<EOF
{  "command":"sourceselect","priority":$prio}
EOF
)

echo "Source select $prio.."
echo $foo
curl -i -H "Content-Type: application/json" -X POST -d "$foo" http://$HOSTHYP:$PORTHYP/json-rpc


