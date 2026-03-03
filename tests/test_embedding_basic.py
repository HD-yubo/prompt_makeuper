"""
Basic test script to verify embedding selector works.
This avoids pytest and complex dependencies.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Test imports
try:
    from app.services.skill_manager import SkillManager
    from app.services.embedding_selector import EmbeddingSkillSelector
    print("Imports OK")
except ImportError as e:
    print(f"Import error: {e}")
    print("\nNote: sentence-transformers needs to be installed.")
    print("Run: pip install sentence-transformers scipy")
    sys.exit(1)

# Test initialization
print("\n--- Testing EmbeddingSkillSelector ---")

skills_dir = Path("app/skills/templates")
skill_manager = SkillManager(skills_dir)
print(f"Loaded {len(skill_manager.list_skills())} skills")

# Create embedding selector
print("Initializing embedding selector (this may take a moment on first run)...")
selector = EmbeddingSkillSelector(skill_manager)

if not selector.is_available():
    print("ERROR: Embedding selector not available")
    print("This usually means sentence-transformers failed to load.")
    sys.exit(1)

print("Embedding selector initialized successfully!")

# Test skill selection
test_prompts = [
    "Make this prompt clearer",
    "Add structure to my prompt",
    "Include examples in this prompt",
    "Add specific constraints",
    "Make this more specific"
]

print("\n--- Testing Skill Selection ---")
for prompt in test_prompts:
    selected = selector.select_skill(prompt)
    print(f"Prompt: '{prompt[:40]}...' -> {selected}")

# Test top-k selection
print("\n--- Testing Top-K Selection ---")
prompt = "Write a clear, specific Python function"
top_k = selector.get_top_k_skills(prompt, k=3)
print(f"Prompt: '{prompt}'")
for i, (skill, score) in enumerate(top_k, 1):
    print(f"  {i}. {skill}: {score:.4f}")

print("\n--- All tests passed! ---")
