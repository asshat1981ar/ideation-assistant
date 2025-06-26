import os
import json
import time
import logging
from huggingface_hub import InferenceClient
from colorama import init, Fore, Style

# Initialize colorama for colored output
init()

class IdeationError(Exception):
    pass

def setup_logging():
    """Set up logging to a file in Termux storage."""
    os.makedirs(os.path.expanduser("~/storage/shared/ideation-assistant"), exist_ok=True)
    logging.basicConfig(
        filename=os.path.expanduser("~/storage/shared/ideation-assistant/log.txt"),
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

def load_config():
    """Load configuration from ~/.ideation_config."""
    config_path = os.path.expanduser("~/.ideation_config")
    config = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "temperature": 0.785,
        "max_retries": 3
    }
    if not os.path.exists(config_path):
        raise IdeationError("Config file ~/.ideation_config not found. Please create it with HF_TOKEN, MODEL, TEMPERATURE, and MAX_RETRIES.")
    with open(config_path, "r") as f:
        for line in f:
            key, value = line.strip().split("=", 1)
            if key == "HF_TOKEN":
                config["token"] = value
            elif key == "MODEL":
                config["model"] = value
            elif key == "TEMPERATURE":
                config["temperature"] = float(value)
            elif key == "MAX_RETRIES":
                config["max_retries"] = int(value)
    if "token" not in config:
        raise IdeationError("HF_TOKEN not found in ~/.ideation_config.")
    logging.info("Configuration loaded successfully")
    return config

def collect_input():
    """Collect project details with real-time validation."""
    project_info = {}
    print(Fore.CYAN + "=== AI-Augmented Ideation Assistant ===")
    while not project_info.get("description"):
        project_info["description"] = input(Fore.GREEN + "Project Description (required): ")
        if not project_info["description"]:
            print(Fore.RED + "Error: Description is required.")
    while not project_info.get("problem"):
        project_info["problem"] = input(Fore.GREEN + "Core Problem (required): ")
        if not project_info["problem"]:
            print(Fore.RED + "Error: Core problem is required.")
    project_info.update({
        "name": input(Fore.GREEN + "Project Name (optional): ") or "your project",
        "audience": input(Fore.GREEN + "Target Audience (optional): ") or "the target audience",
        "knowns": input(Fore.GREEN + "Key Knowns (optional): "),
        "unknowns": input(Fore.GREEN + "Key Unknowns (optional): "),
        "data": input(Fore.GREEN + "Available Data (optional): ")
    })
    logging.info(f"Collected input for project: {project_info['name']}")
    return project_info

def call_hf_api(prompt, config):
    """Reusable function to call Hugging Face API."""
    client = InferenceClient(token=config["token"])
    retries = config["max_retries"]
    while retries > 0:
        try:
            response = client.text_generation(
                model=config["model"],
                prompt=prompt,
                max_new_tokens=1500,
                temperature=config["temperature"],
                return_full_text=False
            )
            logging.info("Successful API call")
            return json.loads(response)
        except Exception as e:
            if "404" in str(e):
                raise IdeationError(f"Model {config['model']} not found. Please check model availability or update ~/.ideation_config with a valid model.")
            retries -= 1
            logging.warning(f"API retry {config['max_retries']-retries}/{config['max_retries']}: {e}")
            time.sleep(5)
            if retries == 0:
                raise IdeationError(f"Max retries exceeded: {e}")

def generate_suggestions(project_info, config):
    """Generate suggestions using Hugging Face API."""
    prompt = f"""
    You are an AI-Augmented Ideation Assistant. Based on the following project details, generate structured suggestions for context, constraints, criteria, personas, and tuning advice. Format the response as a JSON object with keys: context, constraints, criteria, personas, tuning. Each key should contain an array of objects with 'point' and 'augmentation' fields.

    Project Details:
    - Project Name: {project_info['name']}
    - Description: {project_info['description']}
    - Core Problem: {project_info['problem']}
    - Target Audience: {project_info['audience']}
    - Key Knowns: {project_info['knowns']}
    - Key Unknowns: {project_info['unknowns']}
    - Available Data: {project_info['data']}
    """
    try:
        return call_hf_api(prompt, config)
    except json.JSONDecodeError:
        raise IdeationError("Failed to parse API response as JSON.")

def display_suggestions(suggestions, selected_categories=None):
    """Display suggestions in a formatted, colorized manner."""
    if selected_categories is None:
        selected_categories = suggestions.keys()
    print(Fore.CYAN + "\n=== Generated Suggestions ===")
    for category in selected_categories:
        if category in suggestions:
            print(Fore.MAGENTA + f"\n{category.capitalize()}:")
            for i, item in enumerate(suggestions[category], 1):
                print(Fore.WHITE + f"{i}. {item['point']}")
                print(Fore.BLUE + f"   AI Augmentation: {item['augmentation']}")
                logging.info(f"Displayed {category} suggestion: {item['point']}")

def save_suggestions(suggestions, project_name):
    """Save suggestions to a JSON file in Termux storage."""
    output_dir = os.path.expanduser("~/storage/shared/ideation-assistant")
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{output_dir}/{project_name.replace(' ', '_')}_suggestions.json"
    with open(filename, "w") as f:
        json.dump(suggestions, f, indent=2)
    logging.info(f"Suggestions saved to {filename}")
    print(Fore.GREEN + f"Suggestions saved to {filename}")

def main():
    """Main function to run the ideation assistant."""
    setup_logging()
    try:
        config = load_config()
        project_info = collect_input()
        print(Fore.YELLOW + "\nGenerating suggestions...")
        suggestions = generate_suggestions(project_info, config)
        display_suggestions(suggestions)
        save_suggestions(suggestions, project_info["name"])
    except IdeationError as e:
        logging.error(f"Error: {e}")
        print(Fore.RED + f"Error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(Fore.RED + f"Unexpected error: {e}")

if __name__ == "__main__":
    main()