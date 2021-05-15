HOSTHYP="192.168.1.55"
PORTHYP="8090"


clear=$(cat <<EOF
{
  "command":"clear",
  "priority":50,
}
EOF
)


curl -i -H "Content-Type: application/json" -X POST -d "$clear" http://$HOSTHYP:$PORTHYP/json-rpc


