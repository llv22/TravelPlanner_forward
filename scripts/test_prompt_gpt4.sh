#!/bin/bash
set -e
export OUTPUT_DIR=./
# We support MODEL in ['gpt-3.5-turbo-X','gpt-4-1106-preview','gemini','mistral-7B-32K','mixtral']
export MODEL_NAME=gpt-4-1106-preview
#export OPENAI_API_KEY=YOUR_OPENAI_KEY already set in conda
# if you do not want to test google models, like gemini, just input "1".
export GOOGLE_API_KEY=1
# SET_TYPE in ['validation', 'test']
export SET_TYPE=validation
# STRATEGY in ['direct','cot','react','reflexion']
export STRATEGY=direct

python tools/planner/sole_planning.py  --set_type $SET_TYPE --output_dir $OUTPUT_DIR --model_name $MODEL_NAME --strategy $STRATEGY

export OUTPUT_DIR=./evaluation
export TMP_DIR=.
export EVALUATION_DIR=./evaluation
export MODE=sole-planning
export SUBMISSION_FILE_DIR=./postprocess
export STRATEGY=direct

python postprocess/combination.py --set_type $SET_TYPE --output_dir $OUTPUT_DIR --model_name $MODEL_NAME --strategy $STRATEGY --submission_file_dir $SUBMISSION_FILE_DIR --mode $MODE

export EVALUATION_FILE_PATH=../postprocess/validation_gpt-4-1106-preview_direct_sole-planning_submission.jsonl

python evaluation/eval.py --set_type $SET_TYPE --evaluation_file_path $EVALUATION_FILE_PATH
