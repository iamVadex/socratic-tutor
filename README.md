# socratic-tutor
AI-powered e-learning system that teaches students through the Socratic method — guiding them to discover answers via structured questions rather than giving direct answers

# Socratic Tutor — QLoRA Fine-tuned Gemma 2 9B

An AI-powered Socratic tutor built entirely on open-source models with zero paid APIs.
Fine-tuned using QLoRA on Gemma 2 9B to ask guiding questions instead of giving direct answers.

## Approach
The problem with prompting alone: System prompts that say "don't give direct answers" are brittle. Models drift, leak answers mid-conversation, and revert to explanation mode under pressure.
The solution: Fine-tune the behavior into the model weights using QLoRA, so Socratic questioning is intrinsic — not enforced by fragile prompt engineering.
Pipeline overview:
Dataset Generation → QLoRA Fine-tuning → Evaluation → Dialogue Engine → Deployment
      (Phase 1)          (Phase 2)         (Phase 2.6)     (Phase 3)       (Phase 4)

## Project Status
Active development — NIT Calicut B.Tech CSE Internship Project

## Completed
- Custom dataset generation pipeline (489 conversations, 13.7 avg turns)
- QLoRA fine-tuning on Gemma 2 9B (Kaggle T4 x2, loss 5.3 → 0.7)
- Evaluation response generation (base vs fine-tuned, 50 test cases)

## In Progress (evaluation methods not finalized)
- Layer 1 automated evaluation (Socratic Compliance, BERTScore, ROUGE-L ,direct answer,correct answer,response length etc)
- Layer 2 LLM-as-Judge panel (Claude + GPT-4 + Gemini+Llama 3 70B)
- Layer 3 Human evaluation

## Next stages Phase 3 and Phase 4 
- Dialogue Intelligence Engine (struggle detection, hint escalation)
- FastAPI inference server
- Gradio frontend on HuggingFace Spaces
-Report

## Dataset
Generated entirely locally using Ollama (gemma2:9b) on an Acer Predator laptop — no cloud APIs.
Property                     Value
Total conversations           489 (from 525 attempts, 93% acceptance)

Training pairs                3,107

Avg turns per 
conversation                  13.7

Domains                       Physics (200), Biology (129), Math (97), CS (32), Economics (31)

## Model
- Base: google/gemma-2-9b-it
- Method: QLoRA (4-bit NF4, LoRA r=16, alpha=32)
- Trainable params: ~13M / 9B (0.15%)

## Hardware
- Dataset generation: Acer Predator laptop (local Ollama)
- Training: Kaggle T4 x2 GPU (free tier)
- Inference: Kaggle T4 x2 GPU
