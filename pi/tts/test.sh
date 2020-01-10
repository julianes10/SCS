#This is a benchmark 

EXAMPLE_ESP="Hola amigo como estas, la temperatura es de 23 grados" 
EXAMPLE_ENG="Hello my friend, how are you, the temperature is 23 degrees" 
ENG="This is a test in english using " 
ESP="Esto es una prueba en español usando " 


function theTest 
{
 msg1="$ENG $2"
 msg2="$EXAMPLE_ENG"
 if [ $1 == "es" ]; then
   msg1="$ESP $2"
   msg2="$EXAMPLE_ESP"
 fi
 
 echo "$msg1" | $2 $3
 sleep 1
 echo "$msg2" | $2 $3
 sleep 1
}

if [ "$1" == "--all" -o "$1" == "--en" ]; then
  theTest "en" "espeak" "-ven+f3 -k5 -s150" 
  theTest "en" "festival" "--tts" 
  theTest "en" "flite" "" 
  pico2wave -w lookdave.wav "$ENG picowave" && aplay lookdave.wav
  sleep 1
  pico2wave -w lookdave.wav "$EXAMPLE_ENG" && aplay lookdave.wav
  sleep 1
fi

if [ "$1" == "--all" -o "$1" == "--es" ]; then
  theTest "es" "espeak" "-ves+f3 -k5 -s150"
  theTest "es" "festival" "--tts --language spanish" 
  pico2wave -l es-ES -w lookdave.wav "$ESP picowave" && aplay lookdave.wav
  sleep 1
  pico2wave -l es-ES -w lookdave.wav "$EXAMPLE_ESP" && aplay lookdave.wav
  sleep 1
  flite -t "No way of loading voices" 
fi



