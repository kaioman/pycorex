import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from pycorex.utils.prompt_generator import PromptGenerator
from pycorex.utils.pony_prompt_generator import PonyPromptGenerator

PromptGenerator.register_generator("pony", PonyPromptGenerator)

# --- 実行と出力 ---
if __name__ == "__main__":
    json_path = "tests/prompt/persona/Aoi.json"
    
    try:
        generator = PromptGenerator.get_generator(
            "pony",
            api_path="tests/prompt/persona/Aoi.json",
            camera_path="tests/prompt/camera_angules.json",
            wardrobe_path="tests/prompt/wardrobe.json"
        )
        
        # 通常版（Lv1）
        pos_1, neg_e = generator.generate_prompt(level=1)
        # 微エロ版（Lv2）
        pos_2, neg_e = generator.generate_prompt(level=2)
        # 官能版（Lv3）
        pos_3, neg_e = generator.generate_prompt(level=3, target_scene_id="lv3_true_shirt_shredded")
        # 限界突破版（Lv4）
        pos_4, neg_e4 = generator.generate_prompt(level=4, target_scene_id="lv4_phys_torn_ecstasy")
        
        print(f"=== POSITIVE (Level 1) ===\n{pos_1}\n")
        print(f"=== POSITIVE (Level 2) ===\n{pos_2}\n")
        print(f"=== POSITIVE (Level 3) ===\n{pos_3}\n")
        print(f"=== POSITIVE (Level 4) ===\n{pos_4}\n")
        print(f"=== NEGATIVE (Common) ===\n{neg_e}")
        print(f"=== NEGATIVE (Level 4) ===\n{neg_e4}")
        
    except Exception as e:
        print(f"Error: {e}")
