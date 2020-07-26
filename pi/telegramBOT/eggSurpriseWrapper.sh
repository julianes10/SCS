#!/bin/bash 
# unzip incoming file, search for eggSurprise.sh file and execute it
# Useful for uploading new software, config, patching or whatever other suprises
# The force be with you using it.

# For the sake of full output view in non-background call, then exit 0 in any case for debugging
exec > /tmp/eggSurpriseWrapper.log 2>&1
echo "Executing $0 $@..."
date
whoami

usage(){
  echo "------------------------------------------------------------------"
	echo "Usage: $0 <eggSurprise.tgz>"
	exit 1
}


rt=0
INPUTFILE=$1
SUPERNOVA="eggSurprise.sh"
#OUTPATH=`mktemp -d`
OUTPATH=/tmp/egg

cleanup()
{
  echo "Clean up"
  # comment if debugging
  # DON'T DO THIS rm -rf $OUTPATH 
  # Open to discussion rm -r  $INPUTFILE
}

if [ "$#" -ne 1 ]; then
  usage
fi


rm -rf $OUTPATH
mkdir -p $OUTPATH
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
# Even being root blocks somehow in some commanda asking fo root pass. 
# It is not the same in terminal than launched behind telegram daemon
# STUPID ISSUE KILLING Y PARENTS sudo -u pi -- sudo ./$SUPERNOVA
# does not work neidhter./$SUPERNOVA &
touch /tmp/eggIsComing
rt=`echo $?`
echo "===================================="

echo "The surprise is executed $rt. Exiting"
cleanup
#exit $rt
exit 0




