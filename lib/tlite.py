import json
import configparser

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import re

config = configparser.ConfigParser()
config.read("settings.ini")


class TLite:
    def __init__(self):
        torch.manual_seed(42)
        model_name = config['Tlite']['model_path']
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, token=config['Tlite']['token'])
        self.model = AutoModelForCausalLM.from_pretrained(model_name, device_map="cuda:0")

    def send_promt(self, promt):
        messages = [
            {"role": "user", "content": promt},
        ]
        input_ids = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to('cuda:0')
        terminators = [
            self.tokenizer.eos_token_id,
            self.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]
        outputs = self.model.generate(
            input_ids,
            max_new_tokens=3000,
            eos_token_id=terminators,
        )
        text_r = re.sub(r"^user[\s\S]*assistant\n\n", "", self.tokenizer.decode(outputs[0], skip_special_tokens=True))
        text = re.findall(r'^\{\n[\w\W]*\n\}', text_r)
        if len(text) > 0:
            return json.loads(text[0].replace('\n', ''))
        else:
            return {"text": text_r}
