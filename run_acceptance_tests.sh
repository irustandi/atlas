#!/bin/bash


cd testing

for acceptance_directory in $(echo *acceptance)
do
    python -Wi -m unittest -f -v $acceptance_directory
done

cd ../tensorboard
for acceptance_directory in $(echo *acceptance)
do
    python -Wi -m unittest -f -v $acceptance_directory
done