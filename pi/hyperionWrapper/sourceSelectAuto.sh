HOSTHYP="192.168.1.55"
PORTHYP="8090"


foo=$(cat <<EOF
{  "command":"sourceselect","auto":true}
EOF
)

echo "Source select auto.."
echo $foo
curl -i -H "Content-Type: application/json" -X POST -d "$foo" http://$HOSTHYP:$PORTHYP/json-rpc


