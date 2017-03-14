#!/bin/bash

ITEM_URIS=$*
if [ -z "${ITEM_URIS}" ]; then
  ITEM_URIS=`pwd`
fi

for ITEM_URI in ${ITEM_URIS}; do
  ITEM=${ITEM_URI/file:\/\//}
  if [[ "$ITEM" = /* ]]; then
    ABS_PATH=$ITEM
  else 
    ABS_PATH=`pwd`/$ITEM
  fi

  ABS_DIR_PATH=`dirname ${ABS_PATH}`

  HOST=`hostname`
  QS_USER=adiog
  QS_HOST=quicksave.pl
  QS_PATH=/qs/${QS_USER}/host/${HOST}/${ABS_DIR_PATH}

  #assuming that there is a repo in /qs/${QS_USER}/host
  #ssh ${QS_USER}@${QS_HOST} "cd /qs/${QS_USER}/host && [[ ! -d .git ]] && git init"

  ssh ${QS_USER}@${QS_HOST} "mkdir -p ${QS_PATH}" && \
  rsync --progress --delete -avz -e ssh ${ABS_PATH} ${QS_USER}@${QS_HOST}:${QS_PATH} || \
  (notify-send "quicksave.pl" "Item ${ITEM} has not been saved." && FAIL=1)
done

if [[ -z "$FAIL" ]]; then
  ssh ${QS_USER}@${QS_HOST} "cd /qs/${QS_USER}/host && git add . && git commit -m \"qs_sync `date`\"" && \
  notify-send "quicksave.pl" "Item has been saved."
fi

