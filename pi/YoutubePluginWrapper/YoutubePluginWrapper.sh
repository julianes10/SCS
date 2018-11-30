#!/bin/bash 
echo "Wrapper to access youtube plugin in kodi"
echo "Here we go: $@"

################################################
function usage
{ 
  echo  "$0 
           --video-id        <VIDEOID>  
           --search         <QUOTED STRING> <VIDEO ID OUTPUT FILE> 
           --search-random  <QUOTED STRING> <VIDEO ID OUTPUT FILE> 
           --next           <OUTPUT_FILE>  
           --back           <OUTPUT_FILE>  
           --stop  
           --url            <URL> 
           --help"
  echo "Notes:
          --search option will play first item on search results list 
          --search-random option will play random item on search results list 
          --search,--search-random,--back and --stop will save result list and current playing item in  <OUTPUT_FILE> "
}

################################################
function playVideoId 
{
  local temp
  temp="${1%\"}"
  temp="${temp#\"}"

  echo "Asking youtube to play VideoID \"$temp\"..."
  curl -i -X POST http://localhost:8080/jsonrpc  \
    -H "Content-Type: application/json" \
    --data '{ "jsonrpc": "2.0", "method": "Player.Open", "params": [{"file" : "plugin://plugin.video.youtube/?action=play_video&videoid='$temp'"}], "id": 1 }'
}  


################################################
function stopPlayer 
{
  echo "Stopping kodi player..."
  curl -i -X POST http://localhost:8080/jsonrpc  \
    -H "Content-Type: application/json" \
    --data '{ "jsonrpc": "2.0", "method": "Player.Stop", "params": {"playerid":0}, "id": 1 }'
  curl -i -X POST http://localhost:8080/jsonrpc  \
    -H "Content-Type: application/json" \
    --data '{ "jsonrpc": "2.0", "method": "Player.Stop", "params": {"playerid":1}, "id": 1 }'

} 


################################################
### Picked partially from https://stackoverflow.com/questions/296536/how-to-urlencode-data-for-curl-command
function searchString 
{
  local data
  data="$(curl -s -o /dev/null -w %{url_effective} --get --data-urlencode "$1" "")"
  local encoded
  encoded="${data##/?}"
  echo "Searching in Youtube: \"$1\" that is encoded as \"$encoded\"..."
  echo "Saving results in file: \"$2\"..."
  curl -s https://www.youtube.com/results?search_query="$encoded" | sed -ne 's/.*\(data-video-ids="[^ ]*"\).*/\1/p' | sort | uniq > $2
} 

################################################
################################################
################################################
if [ "$1" == "-h" -o "$1" == "--help" ]; then
  usage
  exit 0
elif [ "$1" == "" ]; then
  echo "ERROR, args needed"
  usage
  exit -1
elif [ "$1" == "--stop" ]; then
  stopPlayer
  exit 0
elif [ "$1" == "--url" ]; then
  video=$( echo "$2" | tr '?&#' '\n\n' | grep -e '^v=' | cut -d'=' -f2 )
  playVideoId $video
elif [ "$1" == "--video-id" ]; then
  playVideoId $2
elif [ "$1" == "--search" ]; then
  searchString "$2" "$3" 
  video=$( head -1 $3 | cut -d'=' -f2 )
  sed -i "s/$video/$video PLAYING/" $3
  playVideoId $video
elif [ "$1" == "--search-random" ]; then
  searchString "$2" "$3"
  lines=$( wc -l $3 | cut -d' ' -f1 )
  echo $lines
  export lines
  targetline=$( echo $RANDOM % $lines + 1 | bc )
  video=$( head -$targetline $3 | tail -1 | cut -d'=' -f2 )
  sed -i "s/$video/$video PLAYING/" $3
  playVideoId $video
elif [ "$1" == "--next" ]; then
  video=$( grep " PLAYING" $2 | cut -d'=' -f2 )
  echo "Current video id playing $video..."
  nextvideo=$( grep " PLAYING" -C1 $2 | tail -1 | grep -v " PLAYING" | cut -d'=' -f2 )
  if [ "$nextvideo" == "" ]; then
    echo "Start again from first"
    nextvideo=$( head -1 $2 | cut -d'=' -f2 )
  fi
  sed -i "s/ PLAYING//" $2
  sed -i "s/$nextvideo/$nextvideo PLAYING/" $2
  playVideoId $nextvideo
elif [ "$1" == "--back" ]; then
  video=$( grep " PLAYING" $2 | cut -d'=' -f2 )
  echo "Current video id playing $video..."
  nextvideo=$( grep " PLAYING" -C1 $2 | head -1 | grep -v " PLAYING" | cut -d'=' -f2 )
  if [ "$nextvideo" == "" ]; then
    echo "Start again from last"
    nextvideo=$( tail -1 $2 | cut -d'=' -f2 )
  fi
  sed -i "s/ PLAYING//" $2
  sed -i "s/$nextvideo/$nextvideo PLAYING/" $2
  playVideoId $nextvideo
else
  echo "ERROR, unknown option $1"
  usage
  exit -1
fi






