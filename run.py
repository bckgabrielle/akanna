import argparse
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
KNOWLEDGE_DIR = HERE.parent / "knowledge"
DEFAULT_MODEL = HERE.parent / "model" / "akanna-1.5b-q4_k_m.gguf"

SYSTEM_PREAMBLE = (
    "You are Akanna, an offline farm crisis advisor for smallholder farmers "
    "and agricultural extension officers in Africa. Give short, practical, "
    "low cost steps a farmer can act on today with materials they likely "
    "already have. Be direct about when a problem is serious enough to "
    "contact a local extension or veterinary officer. Do not assume access "
    "to the internet, paid inputs, or specialist equipment unless the "
    "farmer mentions having them."
)


def load_playbooks():
    playbooks = []
    for path in sorted(KNOWLEDGE_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        match = re.search(r"Keywords:\s*(.+)", text)
        keywords = [k.strip().lower() for k in match.group(1).split(",")] if match else []
        playbooks.append({"name": path.stem, "text": text, "keywords": keywords})
    return playbooks


def retrieve(query, playbooks, top_k=1):
    q = query.lower()
    scored = []
    for pb in playbooks:
        score = sum(1 for kw in pb["keywords"] if kw and kw in q)
        if score:
            scored.append((score, pb))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [pb for _, pb in scored[:top_k]] if scored else []


def build_prompt(matched_playbooks):
    system = SYSTEM_PREAMBLE
    if matched_playbooks:
        context = "\n\n".join(pb["text"] for pb in matched_playbooks)
        system += "\n\nUse this reference guidance to ground your answer, in your own words:\n\n" + context
    return system


def run_llama_cpp(model_path, system_prompt, user_query, n_predict=350):
    full_prompt = f"<|system|>\n{system_prompt}\n<|user|>\n{user_query}\n<|assistant|>\n"
    cmd = [
        "llama-cli",
        "-m", str(model_path),
        "-p", full_prompt,
        "-n", str(n_predict),
        "--temp", "0.4",
        "-no-cnv",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except FileNotFoundError:
        sys.exit("llama-cli was not found on PATH. Install llama.cpp first.")
    except subprocess.CalledProcessError as e:
        sys.exit(f"llama-cli exited with an error:\n{e.stderr}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--model", default=str(DEFAULT_MODEL))
    parser.add_argument("--n-predict", type=int, default=350)
    args = parser.parse_args()

    playbooks = load_playbooks()
    matched = retrieve(args.query, playbooks, top_k=1)
    system_prompt = build_prompt(matched)

    if matched:
        print(f"retrieved playbook: {matched[0]['name']}", file=sys.stderr)
    else:
        print("no playbook matched, answering from general model knowledge", file=sys.stderr)

    output = run_llama_cpp(args.model, system_prompt, args.query, args.n_predict)
    print(output)


if __name__ == "__main__":
    main()
