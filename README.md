<h1 align="center">Smart Language Agents in Real-World Planning </h1>

![Travel Planner](https://img.shields.io/badge/Task-Planning-blue)
![Travel Planner](https://img.shields.io/badge/Task-Tool_Use-blue) 
![Travel Planner](https://img.shields.io/badge/Task-Language_Agents-blue)  
![GPT-4](https://img.shields.io/badge/Model-GPT--4-green) 
![LLMs](https://img.shields.io/badge/Model-LLMs-green)

<p align="center">
    <img src="images/icon.png" width="10%"> <br>
</p>

Code for the Paper "Smart Language Agents in Real-World Planning" (Under Review), based on the paper [TravelPlanner: A Benchmark for Real-World Planning with Language Agents](http://arxiv.org/abs/2402.01622)".

![Demo Video GIF](images/TravelPlanner.gif)

<p align="center">
[<a href="https://osu-nlp-group.github.io/TravelPlanner/">Website</a>]•
[<a href="http://arxiv.org/abs/2402.01622">Paper</a>] •
[<a href="https://huggingface.co/datasets/osunlp/TravelPlanner">Dataset</a>] •
[<a href="https://huggingface.co/spaces/osunlp/TravelPlannerLeaderboard">Leaderboard</a>] •
[<a href="https://huggingface.co/spaces/osunlp/TravelPlannerEnvironment">Environment</a>] •
[<a href="https://twitter.com/ysu_nlp/status/1754365367294562680">Twitter</a>]
</p>



# TravelPlanner

TravelPlanner is a benchmark crafted for evaluating language agents in tool-use and complex planning within multiple constraints.

For a given query, language agents are expected to formulate a comprehensive plan that includes transportation, daily meals, attractions, and accommodation for each day.

For constraints, from the perspective of real world applications, TravelPlanner includes three types of them: Environment Constraint, Commonsense Constraint, and Hard Constraint. 


## Setup Environment

1. Create a conda environment and install dependency:
```bash
conda create -n travelplanner python=3.9
conda activate travelplanner
pip install -r requirements.txt
```

2. Download the [database](https://drive.google.com/file/d/1pF1Sw6pBmq2sFkJvm-LzJOqrmfWoQgxE/view?usp=drive_link) and unzip it to the `TravelPlanner` directory (i.e., `your/path/TravelPlanner`).

## Running
### Two-stage Mode

In the two-stage mode, language agents are tasked to with employing various search tools to gather information.
Based on the collected information, language agents are expected to deliver a plan that not only meet the user’s needs specified in the query but also adheres to commonsense constraints.

```bash
export OUTPUT_DIR=path/to/your/output/file
# We support MODEL in ['gpt-3.5-turbo-X','gpt-4-1106-preview','gemini','mistral-7B-32K','mixtral']
export MODEL_NAME=MODEL_NAME
export OPENAI_API_KEY=YOUR_OPENAI_KEY
# if you do not want to test google models, like gemini, just input "1".
export GOOGLE_API_KEY=YOUR_GOOGLE_KEY
# SET_TYPE in ['validation', 'test']
export SET_TYPE=validation
cd agents
python tool_agents.py  --set_type $SET_TYPE --output_dir $OUTPUT_DIR --model_name $MODEL_NAME
```
The generated plan will be stored in OUTPUT_DIR/SET_TYPE.

### Sole-Planning Mode

TravelPlanner also provides an easier mode solely focused on testing their planning ability.
The sole-planning mode ensures that no crucial information is missed, thereby enabling agents to focus on planning itself.

Please refer to paper for more details.

```bash
export OUTPUT_DIR=path/to/your/output/file
# We support MODEL in ['gpt-3.5-turbo-X','gpt-4-1106-preview','gemini','mistral-7B-32K','mixtral']
export MODEL_NAME=MODEL_NAME
export OPENAI_API_KEY=YOUR_OPENAI_KEY
# if you do not want to test google models, like gemini, just input "1".
export GOOGLE_API_KEY=YOUR_GOOGLE_KEY
# SET_TYPE in ['validation', 'test']
export SET_TYPE=validation
# STRATEGY in ['direct','cot','react','reflexion', 'by_day']
export STRATEGY=direct

cd tools/planner
python sole_planning.py  --set_type $SET_TYPE --output_dir $OUTPUT_DIR --model_name $MODEL_NAME --strategy $STRATEGY
```

## Postprocess

In order to parse natural language plans, we use gpt-4 to convert these plans into json formats. We encourage developers to try different parsing prompts to obtain better-formatted plans.

```bash
export OUTPUT_DIR=../evaluation
export MODEL_NAME=gpt-4-1106-preview
export SET_TYPE=validation
export STRATEGY=direct
export TMP_DIR=.
export EVALUATION_DIR=../evaluation
export MODE=sole-planning
export SUBMISSION_FILE_DIR=./

cd postprocess
python parsing.py  --set_type $SET_TYPE --output_dir $OUTPUT_DIR --model_name $MODEL_NAME --strategy $STRATEGY --tmp_dir $TMP_DIR --mode $MODE

# Then these parsed plans should be stored as the real json formats.
python element_extraction.py  --set_type $SET_TYPE --output_dir $OUTPUT_DIR --model_name $MODEL_NAME --strategy $STRATEGY --tmp_dir $TMP_DIR --mode $MODE

# Finally, combine these plan files for evaluation. We also provide a evaluation example file "example_evaluation.jsonl" in the postprocess folder.
python combination.py --set_type $SET_TYPE --output_dir $OUTPUT_DIR --model_name $MODEL_NAME --strategy $STRATEGY --submission_file_dir $SUBMISSION_FILE_DIR --mode $MODE
```

## Evaluation

We support the offline validation set evaluation through the provided evaluation script. To avoid data contamination, please use our official [leaderboard](https://huggingface.co/spaces/osunlp/TravelPlannerLeaderboard) for test set evaluation.

```bash
export SET_TYPE=validation
export EVALUATION_FILE_PATH=../postprocess/validation_gpt-4-1106-preview_direct_sole-planning_submission.jsonl

cd evaluation
python eval.py --set_type $SET_TYPE --evaluation_file_path $EVALUATION_FILE_PATH
```

## Load Datasets

```python
from datasets import load_dataset
# test can be substituted by "train" and "validation".
data = load_dataset('osunlp/TravelPlanner','test')['test']
```

## Contact

If you have any problems, please contact 
[Timothy Wei](mailto:timswei@gmail.com)