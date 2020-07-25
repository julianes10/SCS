#!/bin/bash 
# unzip incoming file, search for eggSurprise.sh file and execute it
# Useful for uploading new software, config, patching or whatever other suprises
# The force be with you using it.

# For the sake of full output view in non-background call, then exit 0 in any case for debugging

echo "Executing $0 $@..."
usage(){
  echo "------------------------------------------------------------------"
	echo "Usage: $0 <eggSurprise.tgz>"
	exit 1
}


rt=0
INPUTFILE=$1
SUPERNOVA="eggSurprise.sh"
OUTPATH=`mktemp -d`


cleanup()
{
  # comment if debugging
  rm -rf $OUTPATH 
  # Open to discussion rm -r  $INPUTFILE
}

if [ "$#" -ne 1 ]; then
  usage
fi

tar -C $OUTPATH -xzvf $INPUTFILE
rt=`echo $?`

if [ "$rt" != "0" ]; then
  echo "This egg is not for me. Exiting"
  cleanup
  exit <0  #for debugging in through telegram
fi

cd $OUTPATH
if [[ ! -x $SUPERNOVA ]]
then
  echo "This egg is not a surprise. Exiting"
  cleanup
  exit 0  #for debugging in through telegram
fi

echo "This egg is for me, just jumping..."
echo "===================================="
./$SUPERNOVA
rt=`echo $?`
echo "===================================="

echo "The surprise is executed $rt. Exiting"
cleanup
#exit $rt
exit 0




