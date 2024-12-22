from dataclasses import dataclass, field
from typing import Dict, List, Optional 
import ipywidgets as widgets
from IPython.display import display, clear_output

@dataclass
class ModelBlocks:
    blocks: Dict[str, List[List[str]]] = field(default_factory=dict)
    
    def add_block(self, block_name: str, block_content: List[str]):
        if block_name not in self.blocks:
            self.blocks[block_name] = []
        self.blocks[block_name].append(block_content)
    
    def update_block(self, block_name: str, new_content: List[str]):
        if block_name in self.blocks:
            self.blocks[block_name] = new_content
        else:
            raise ValueError(f"Block '{block_name}' not found in model.")
    
    def render(self) -> str:
        sections = []
        for block_name, contents in self.blocks.items():
            for content in contents:
                sections.extend(content)
            sections.append("\n")
        return "".join(sections).strip()
    

def parse_control_file(file_path: str) -> ModelBlocks:
    model_blocks = ModelBlocks()
    with open(file_path, "r") as file:
        lines = file.readlines()
    
    current_block = None
    block_content = []
    for line in lines:
        if line.strip().startswith("$"):
            if current_block:
                model_blocks.add_block(current_block, block_content)
            current_block = line.strip().split()[0]
            block_content = [line]
        elif current_block:
            block_content.append(line)
        else:
            continue
    if current_block:
        model_blocks.add_block(current_block, block_content)
    
    return model_blocks


def widget_edit_block(block_content: List[str], save_callback=None):
    flattened_block_content = [item for sublist in block_content for item in sublist]
    textarea = widgets.Textarea(
        value="".join(flattened_block_content),
        placeholder="Edit block content here...",
        layout=widgets.Layout(width="100%", height="100px")
    )
    save_button = widgets.Button(description="Save", button_style="success")
    output = widgets.Output()
    
    def on_save_clicked(_):
        updated_content = textarea.value
        with output:
            clear_output(wait=True)
            print("Changes saved!")
        if save_callback:
            save_callback(updated_content)
    
    save_button.on_click(on_save_clicked)
    display(widgets.VBox([textarea, save_button, output]))
    

def edit_model_block(model_blocks: ModelBlocks, block_name: str):
    if block_name not in model_blocks.blocks:
        raise ValueError(f"Block '{block_name}' not found in model.")
    
    block_content = model_blocks.blocks[block_name]
    
    def save_callback(updated_content):
        model_blocks.update_block(block_name, updated_content.splitlines(keepends=True))
        print(f"Block '{block_name}' updated.")
    
    widget_edit_block(block_content, save_callback=save_callback)
    
    
def save_control_file(model_blocks: ModelBlocks, file_path: str):
    with open(file_path, "w") as file:
        file.write(model_blocks.render())
    print(f"Control file saved to '{file_path}'.")
