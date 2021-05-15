HOSTHYP="192.168.1.55"
PORTHYP="8090"

color=$3
foo=$(cat <<EOF
{ 
  "command":"color",
  "color":[$color],
  "priority":50,
  "origin":"My Color"
}
EOF
)

auto=$(cat <<EOF
{  "command":"sourceselect","auto":true}
EOF
)


echo "Source select auto.."
echo $foo
curl -i -H "Content-Type: application/json" -X POST -d "$auto" http://$HOSTHYP:$PORTHYP/json-rpc
curl -i -H "Content-Type: application/json" -X POST -d "$foo"  http://$HOSTHYP:$PORTHYP/json-rpc



