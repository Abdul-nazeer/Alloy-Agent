"""
Upload fine-tuned model to Hugging Face Hub for easy demo/sharing.
Run after training completes.
"""

import os
from huggingface_hub import HfApi, login
from pathlib import Path

def push_model_to_hub(
    model_path: str = "./phi3-steel-maintenance/final",
    repo_name: str = "phi3-steel-maintenance",
    username: str = None
):
    """
    Push model to Hugging Face Hub.
    
    Args:
        model_path: Local path to saved model
        repo_name: Repository name on Hub
        username: Your HF username (optional, uses logged-in user)
    """
    
    # Login (run once)
    print("Logging in to Hugging Face...")
    print("Get your token from: https://huggingface.co/settings/tokens")
    login()  # Will prompt for token
    
    api = HfApi()
    
    # Get username if not provided
    if username is None:
        user_info = api.whoami()
        username = user_info['name']
    
    repo_id = f"{username}/{repo_name}"
    
    print(f"\nUploading model to: {repo_id}")
    print("This may take a few minutes...")
    
    try:
        # Create repo if doesn't exist
        api.create_repo(
            repo_id=repo_id,
            private=False,  # Make public for demo
            exist_ok=True
        )
        
        # Upload model files
        api.upload_folder(
            folder_path=model_path,
            repo_id=repo_id,
            repo_type="model"
        )
        
        print(f"\n✅ Model uploaded successfully!")
        print(f"🔗 View at: https://huggingface.co/{repo_id}")
        print(f"\n📝 To use:")
        print(f"   from peft import PeftModel")
        print(f"   model = PeftModel.from_pretrained(")
        print(f"       'microsoft/Phi-3-mini-4k-instruct',")
        print(f"       '{repo_id}'")
        print(f"   )")
        
    except Exception as e:
        print(f"❌ Error uploading: {e}")
        print("Make sure you have write access and the token is valid.")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Upload model to Hugging Face Hub")
    parser.add_argument("--model-path", default="./phi3-steel-maintenance/final", 
                       help="Path to saved model")
    parser.add_argument("--repo-name", default="phi3-steel-maintenance",
                       help="Repository name on Hub")
    parser.add_argument("--username", default=None,
                       help="HuggingFace username (optional)")
    
    args = parser.parse_args()
    
    push_model_to_hub(
        model_path=args.model_path,
        repo_name=args.repo_name,
        username=args.username
    )
