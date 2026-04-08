import os
import time
import json
import random
import pycorex.configs.app_init as app
from pycorex.gemini_client import GeminiClient
from pycorex.uwgen_client import UwgenClient
from pycorex.exceptions.no_candidates_error import NoCandidatesError

def load_config(file_path='config.json'):
    with open(file_path, 'r') as f:
        return json.load(f)

def generate_prompt(config, angle_id=None):
    prompts = []
    
    hair_list = config['hair_styles'].copy()
    outfit_list = config['outfits'].copy()
    nuances = config['view_nuances'].copy()
    cameras = config['camera_types'].copy()
    
    random.shuffle(hair_list)
    random.shuffle(outfit_list)
    
    if angle_id:
        target_angles = [a for a in config['angles'] if a.get('id') == angle_id]
    else:
        target_angles = config['angles']
    
    global_idx = 0
    for angle_data in target_angles:
        
        num_to_generate = angle_data.get('count', 1)
        prefix = angle_data.get('prefix', config.get('prefix', ''))
        cam_type = angle_data.get('camera_type', 'close')
        available_cameras = cameras.get(cam_type, cameras['close'])

        for _ in range(num_to_generate):
            hair = hair_list[global_idx % len(hair_list)]
            outfit = outfit_list[global_idx % len(outfit_list)]
            nuance = random.choice(nuances)
            camera = random.choice(available_cameras)
            
            prompt = config['template'].format(
                prefix=prefix,
                hair=hair,
                outfit=outfit,
                core_item=config['core_item'],
                detail=angle_data['detail'],
                angle=angle_data['angle'],
                nuance=nuance,
                camera=camera,
                style=config['style']
            )
            prompts.append(prompt)
            global_idx += 1

    return prompts

def main(prompt_only=False, angle_id=None):
    
    config_path = 'tests/prompt/lora/config.json'
    if os.path.exists(config_path):
        config = load_config(config_path)
        results = generate_prompt(config, angle_id=angle_id)
        if prompt_only:
            print(results)
            return

        # アプリ初期化
        app.init_app(__file__, "logger.json", "pycorex.json")

        # UwgenClientを初期化
        client = UwgenClient()

        # 元画像取得
        source_file_path = client.get_source_file_path("tests/source_image", "unchain8-2.png")
        
        for idx, prompt in enumerate(results, 1):            
            try:
                # 画像生成を実行
                result = client.edit_image(
                    prompt=prompt,
                    source_image_path=source_file_path,
                    model=GeminiClient.GeminiModel.GEMINI_2_5_FLASH_IMAGE.value,
                    resolution=GeminiClient.ImageSize.TWO_K.value,
                    aspect=GeminiClient.AspectRatio.SQUARE.value,
                    safety_filter = GeminiClient.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT.value,
                    safety_level = GeminiClient.SafetyFilterLevel.BLOCK_ONLY_HIGH.value
                )
                
                # 画像ファイルを出力する
                client.output_images(result["images"], "gen_images")

            except NoCandidatesError as e:
                print(f"Image generation failed: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")

if __name__ == "__main__":
    #main(prompt_only=False, angle_id="high")
    #time.sleep(2)
    #main(prompt_only=False, angle_id="three-quarter")
    #time.sleep(2)
    main(prompt_only=False, angle_id="low")
