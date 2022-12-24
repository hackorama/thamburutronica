TS=`date '+%Y%m%d.%H%M%S'`
cd ../../../..
tar --exclude-vcs --exclude 'thamburutronica/src/device/venv' --exclude 'thamburutronica/src/microcontroller/venv' --exclude 'thamburutronica/src/mobile/venv' --exclude 'thamburutronica/src/mobile/.mypy_cache' -cvf thamburutronica.$TS.tar thamburutronica
cd -
