FOLDER=Desktop/LIRC
PI_HOST=pi@192.168.1.188
FILE=main1.py

scp gpio.py $FILE "$PI_HOST:$FOLDER"
#ssh "$PI_HOST" "cd $FOLDER && sudo python $FILE"
