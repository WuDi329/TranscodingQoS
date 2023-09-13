# echo "start transcoding" >> /home/wd/desktop/VideoQuality/log.txt
# echo "$1" >> /home/wd/desktop/VideoQuality/para.txt
# echo $SHELL >> /home/wd/desktop/VideoQuality/shell.txt
# source ~/miniconda3/etc/profile.d/conda.sh
# conda activate py3810
cd /home/wd/desktop/VideoQuality/
bash -c "/home/wd/miniconda3/envs/py3810/bin/python /home/wd/desktop/VideoQuality/live.py $1 > output.log";
# echo "end transcoding" >> /home/wd/desktop/VideoQuality/log-end2.txt