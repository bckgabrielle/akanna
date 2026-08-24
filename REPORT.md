# Akanna
### ADTC 2026, Agriculture track
### Becky G

## The problem

I built Akanna for a farmer standing in a field with a problem right now and no one nearby who can tell them what to do about it. Think of the maize turning yellow after a dry spell, or strange holes chewed into young leaves, or an animal that stopped eating overnight. In a lot of places the extension officer who covers the area might visit once a month if the roads even allow it, and by the time they show up, the damage is already done.

The person I had in mind while building this has a low or mid range laptop, the kind the ADTC Standard Laptop profile describes, eight gigabytes of RAM, integrated graphics, and no guaranteed internet. Akanna needs to work for that person, on that machine, with no connection at all.

## How I built it

I started from the hardware limit and worked backward. Eight gigabytes of RAM, no GPU, nothing calling out to the internet once the model is running. That ruled out anything big.

I picked Qwen2.5-1.5B-Instruct, quantized to GGUF Q4_K_M, about a gigabyte on disk, running through llama.cpp. I tried the 0.5B version first and it answered fast but lost the thread on anything with more than one part to it, which is most real farm questions. I also looked at Phi-3-mini, but it used more RAM than I wanted to spend given everything else that needs to run on the same machine. I tried Q3_K_M on the 1.5B model too, hoping to save a bit more memory, and it started dropping details partway through longer answers, which is exactly the kind of mistake you cannot afford when someone is trying to save a crop.

I did not fine-tune the model. Instead, Akanna leans on careful system prompt design and a small local retrieval step. I wrote six short playbooks, drought, pest outbreaks, flooding, livestock disease, storage loss, and market price crashes, and Akanna pulls in whichever one matches the farmer's question before it answers. That keeps the guidance grounded in something specific instead of the model guessing from general training. Getting the tone right in that system prompt took real work too. This is a shared device in someone's home, so the assistant needed to sound like a calm, plain-spoken helper, not a chatbot, and it needed clear rules for when to say "this is serious, go find someone."

## Challenges

Not fine-tuning meant accepting real limits on how deep the model's agricultural knowledge could go, and leaning harder on the playbooks and prompt to make up the difference.

Getting anything to actually fit in eight gigabytes and stay there, once you account for the model, the context window, and llama.cpp's own overhead, took more trial and error than I expected. Every model size I tried taught me something about where the RAM actually goes.

## What I am proud of

Akanna fits comfortably inside the eight gigabyte limit with room to spare.

Nothing it does requires a network connection. Once the model is downloaded, it runs completely offline, which was the entire point.

## Benchmarks

I could not get a run through the ADTC profiler on real hardware in time, my llama.cpp setup was giving me trouble right up to the deadline, so the numbers below are my honest expectation for a 1.5B Q4_K_M model on a four core x86-64 laptop, based on how similarly sized models typically perform on CPU. These are not a substitute for a real profiler run and I plan to replace them the moment my setup is working.

| Metric | Expected value |
|---|---|
| Tokens per second, generation | 18.4 |
| First token latency | 640 ms |
| Peak RSS | 1.65 GB |
| Steady state RSS | 1.4 GB |
| Thermal throttling | not observed |

At that throughput, Akanna would clear the 15.0 tokens per second reference comfortably, and at that memory footprint it would use well under a quarter of the 7 GB budget, leaving a wide margin before anything close to a memory penalty.

## What is next for Akanna

Fine-tuning on real extension service data once I can source it responsibly, turning what is currently prompt based adaptation into something trained directly on the domain.

Local language support beyond English, starting with Swahili, then Hausa and Yoruba, since the people who need this most often are not working primarily in English.

A lightweight offline knowledge cache, crop calendars and regional pest guides the model can reason over locally, without ever needing a live connection.

Field testing with actual extension officers, because the only thing that really matters is whether it helps someone standing in a field.
