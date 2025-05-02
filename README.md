# AutoBridge: Automating Smart Device Integration with Centralized Platform

AutoBridge is an LLM-based workflow we introduce that serves as a bridge between smart devices and home management platforms, automatically generating the integration code for each device on the target platform.

---

## 1. Setup

All experiments in this work were conducted on an Ubuntu 22.04 LTS machine equipped with a 2.10 GHz 13th Gen Intel Core i7-13700 CPU. For platform-specific environments and development guidelines, please refer to the official documentation:

- [Home Assistant Developer Docs](https://developers.home-assistant.io/)  
- [OpenHAB Developer Guide](https://www.openhab.org/docs/developer/)  
and other official focumentation for your targeted platform.

---

## 2. AutoBridge Directory

This folder contains the configurations needed to reproduce our work. The backbone model used for our benchmarks is **GPT-4 (v2024.02)**. We use:

- `text-embedding-ada-002` (1,536 dimensions) for textual embeddings  
- `code-search-bge-base` (768 dimensions) for code snippet embeddings  

Each embedding type is indexed with its own FAISS instance.

---

## 3. Benchmark Directory

- **EvalSet 1: RealHardware**  
  Integration code for smart devices tested on real hardware.

- **EvalSet 2: HumanExpertCode**  
  Integration code written by human experts.

---

## 4. User_Study Directory

- **Task A1 (Reference)**  
  Standard implementation for the self-developed smart thermo-hygrometer device.

- **Participant Submissions**  
  Final code submissions from each participant for Task A1 and Task B1, organized by participant ID.
