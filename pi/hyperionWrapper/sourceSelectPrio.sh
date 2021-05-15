HOSTHYP="192.168.1.55"
PORTHYP="8090"

prio=$3
foo=$(cat <<EOF
{  "command":"sourceselect","priority":$prio}
EOF
)

clear=$(cat <<EOF
{
  "command":"clear",
  "priority":50,
}
EOF
)


echo "Source select $prio.."
echo $foo
curl -i -H "Content-Type: application/json" -X POST -d "$clear" http://$HOSTHYP:$PORTHYP/json-rpc
curl -i -H "Content-Type: application/json" -X POST -d "$foo" http://$HOSTHYP:$PORTHYP/json-rpc


