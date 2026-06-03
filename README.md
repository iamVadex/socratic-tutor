# socratic-tutor
AI-powered e-learning system that teaches students through the Socratic method — guiding them to discover answers via structured questions rather than giving direct answers

# Socratic Tutor — QLoRA Fine-tuned Gemma 2 9B

An AI-powered Socratic tutor built entirely on open-source models with zero paid APIs.
Fine-tuned using QLoRA on Gemma 2 9B to ask guiding questions instead of giving direct answers.

## Project Status
Active development — NIT Calicut B.Tech CSE Internship Project

## Completed
- Custom dataset generation pipeline (489 conversations, 13.7 avg turns)
- QLoRA fine-tuning on Gemma 2 9B (Kaggle T4 x2, loss 5.3 → 0.7)
- Evaluation response generation (base vs fine-tuned, 50 test cases)

## In Progress
- Layer 1 automated evaluation (Socratic Compliance, BERTScore, ROUGE-L ,direct answer,correct answer,response length etc)
- Layer 2 LLM-as-Judge panel (Claude + GPT-4 + Gemini+Llama 3 70B)
- Layer 3 Human evaluation

## Next stages Phase 3 and Phase 4 
- Dialogue Intelligence Engine (struggle detection, hint escalation)
- FastAPI inference server
- Gradio frontend on HuggingFace Spaces
-Report

## Dataset
- Domains: Physics, Biology, Math, Economics, CS
- 489 conversations, 3,107 training pairs
- Generated using Ollama (gemma2:9b) locally

## Model
- Base: google/gemma-2-9b-it
- Method: QLoRA (4-bit NF4, LoRA r=16, alpha=32)
- Trainable params: ~13M / 9B (0.15%)

## Hardware
- Dataset generation: Acer Predator laptop (local Ollama)
- Training: Kaggle T4 x2 GPU (free tier)
- Inference: Kaggle T4 x2 GPU
