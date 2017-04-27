#!/bin/bash

CONTAINER="seed_cell_size_2d-development"
DATADIR=/Users/hartleym/data_repo
touch `pwd`/bash_history
docker run -it --rm -v `pwd`/bash_history:/root/.bash_history -v $DATADIR:/data:ro -v `pwd`/scripts:/scripts:ro -v `pwd`/output:/output $CONTAINER
